#!/usr/bin/env python3
# Author: Most of the code is refactored code by Steve Schulze (steve.schulze@fysik.su.se)
# License: BSD-3-Clause

import datetime
import logging
import warnings

import astroplan as ap  # type: ignore
import astropy  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import numpy as np
from astroplan import moon as apmoon  # type: ignore
from astroplan.plots import plot_airmass, plot_altitude  # type: ignore
from astropy import units as u  # type: ignore
from astropy.coordinates import AltAz, EarthLocation, SkyCoord, get_body  # type: ignore
from astropy.time import Time  # type: ignore
from betternot.io import get_date_dir, load_config


class Observability:
    def __init__(self, ztf_ids, date: str | None = None, site: str = "not"):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        self.ztf_ids = ztf_ids

        if date is None:
            self.date = datetime.date.today().strftime("%Y-%m-%d")
        else:
            self.date = date

        self.config = load_config()
        self.site = EarthLocation.of_site(self.config["sites"][site]["short"])
        self.target_dict = {}
        self.logger.info(
            f"Getting observation data for {', '.join(ztf_ids)} for the {self.config['sites'][site]['pretty']}. Chosen date: {self.date}"
        )

    def get_info(self):
        from betternot.fritz import radec, latest_photometry

        for ztf_id in self.ztf_ids:
            if ztf_id not in self.target_dict.keys():
                ra, dec = radec(ztf_id)
                mag, mjd, band = latest_photometry(ztf_id)

                if ra is None:
                    self.logger.info(f"Source {ztf_id} not found on Fritz, skipping.")
                else:
                    self.target_dict.update(
                        {
                            ztf_id: {
                                "ra": ra,
                                "dec": dec,
                                "mag": mag,
                                "mjd": mjd,
                                "band": band,
                            }
                        }
                    )

    def print_info(self):
        self.get_info()

        for ztf_id, info in self.target_dict.items():
            now = Time.now().mjd
            days_ago = now - info["mjd"]

            print("-------------------------------------------")
            print(ztf_id)
            print(f"RA: {info['ra']}")
            print(f"Dec: {info['dec']}")
            print(
                f"{info['mag']:.2f} mag {days_ago:.0f} days ago in the {info['band']} filter"
            )
            print("-------------------------------------------")

    def plot_standards(self):
        std_dict = self.config["standards"]
        self.create_plot(target_dict=std_dict, savename="standards")

    def plot_targets(self):
        self.get_info()

        self.create_plot(
            target_dict=self.target_dict, savename="targets", plot_moon=True
        )

    def create_plot(self, target_dict: dict, savename: str, plot_moon: bool = False):
        target_list = list(target_dict)
        label_size = 14

        plt.figure(figsize=(width := 9, width / 1.61))
        ax = plt.subplot(111)

        self.midnight_utc = Time(self.date, format="isot", scale="utc") + (1 * u.hour)
        delta_midnight = np.linspace(-12, 12, 1000) * u.hour

        frame_time = AltAz(
            obstime=self.midnight_utc + delta_midnight, location=self.site
        )

        for target in target_list:
            if isinstance(target_dict[target]["ra"], str):
                coords = SkyCoord(
                    target_dict[target]["ra"],
                    target_dict[target]["dec"],
                    unit=(u.hour, u.deg),
                )
            else:
                coords = SkyCoord(
                    target_dict[target]["ra"],
                    target_dict[target]["dec"],
                    unit=(u.deg, u.deg),
                )

            obj_altazs = coords.transform_to(frame_time)
            # obj_airmass = obj_altazs.secz

            if plot_moon:
                moon_info = self.check_moon(coords=coords)
                label = f"{target} (moon dist: {moon_info['sep']:.0f}°)"
                illumsymbol = self.get_moon_emoticon(moon_info=moon_info)
            else:
                label = target
            # mask = (obj_airmass > 0) & (obj_airmass < 5)

            ax.plot(
                delta_midnight,
                obj_altazs.alt,
                label=label,
                lw=2,
            )

        sunaltazs = get_body("sun", self.midnight_utc + delta_midnight).transform_to(
            frame_time
        )

        if plot_moon:
            moonaltazs = get_body(
                "moon", self.midnight_utc + delta_midnight
            ).transform_to(frame_time)
            ax.plot(delta_midnight, moonaltazs.alt, lw=2, color="white")

        for sunheight, alpha in [(-0, 0.2), (-18, 1)]:
            ax.fill_between(
                x=delta_midnight.value,
                y1=(0 * u.deg).value,
                y2=(90 * u.deg).value,
                where=sunaltazs.alt.value < (sunheight * u.deg).value,
                color="navy",
                zorder=0,
                alpha=alpha,
            )

        # Plot an airmass scale
        ax2 = ax.secondary_yaxis(
            "right", functions=(self.altitude_to_airmass, self.airmass_to_altitude)
        )
        altitude_ticks = np.linspace(10, 90, 9)
        airmass_ticks = np.round(self.altitude_to_airmass(altitude_ticks), 2)
        ax2.set_yticks(airmass_ticks)
        ax2.set_ylabel("Airmass", fontsize=label_size)

        ax.axvline(x=0, color="white", lw=1)
        ax.axhline(90 - np.arccos(1 / 2.0) * 180 / np.pi, color="#C02F1D")
        ax.axhline(90 - np.arccos(1 / 3.0) * 180 / np.pi, color="#C02F1D", ls="--")

        xmin, xmax = -6, 8

        ax.set_xlim((xmin * u.hour).value, (xmax * u.hour).value)

        labels = [
            "{:.0f} h".format(x + 24) if x < 0 else "{:.0f} h".format(x)
            for x in (np.arange(xmax - xmin) + xmin)
        ]

        ax.set_xticks(
            ((np.arange(xmax - xmin) + xmin) * u.hour).value, labels=labels, rotation=45
        )

        ax.set_ylim((10 * u.deg).value, (90 * u.deg).value)

        ax.set_xlabel("Universal time", fontsize=label_size)
        ax.set_ylabel("Altitude", fontsize=label_size)

        title = f"{self.date} → {(Time(self.date) + (1 * u.day)).isot.split('T')[0]}"

        if plot_moon:
            title += f" {illumsymbol} ({moon_info['illum']:.0f} %)"

            ax.set_title(
                title,
                fontsize=label_size,
            )

        plt.grid(True, color="gray", linestyle="dotted", which="both", alpha=0.5)
        plt.legend()

        outdir = get_date_dir(self.date)
        outpath = outdir / f"{savename}.pdf"

        plt.savefig(outpath, bbox_inches="tight")
        plt.close()

    def check_moon(self, coords):
        """
        Check proximity to the moon and moon illuminated fraction
        """
        moon = get_body("moon", self.midnight_utc, self.site)
        moon_sep = moon.separation(coords)
        illumination = apmoon.moon_illumination(self.midnight_utc)
        illumination_earlier = apmoon.moon_illumination(self.midnight_utc - (2 * u.day))
        illumination_later = apmoon.moon_illumination(self.midnight_utc + (2 * u.day))

        return {
            "sep": moon_sep.to(u.degree).value,
            "illum": illumination * 100,
            "illum-2": illumination_earlier,
            "illum+2": illumination_later,
        }

    @staticmethod
    def altitude_to_airmass(airmass: float):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            altitude = 1.0 / np.cos(np.radians(90 - airmass))
        return altitude

    @staticmethod
    def airmass_to_altitude(altitude: float):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            airmass = 90 - np.degrees(np.arccos(1 / altitude))
        return airmass

    @staticmethod
    def get_moon_emoticon(moon_info: dict):
        illum = moon_info["illum"]
        illum_earlier = moon_info["illum-2"]
        illum_later = moon_info["illum+2"]
        if illum_later - illum_earlier > 0:
            waxing = True
        else:
            waxing = False
        if illum < 16.6:
            symbol = "🌑"
        elif illum < 33.3:
            if waxing:
                symbol = "🌒"
            else:
                symbol = "🌘"
        elif illum < 66.6:
            if waxing:
                symbol = "🌓"
            else:
                symbol = "🌗"
        elif illum < 83:
            if waxing:
                symbol = "🌔"
            else:
                symbol = "🌖"
        else:
            symbol = "🌕"

        return symbol
