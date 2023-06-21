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
        self.logger.info(
            f"Getting observation data for {', '.join(ztf_ids)} for the {self.config['sites'][site]['pretty']}. Chosen date: {self.date}"
        )

    def plot_standards(self):
        std_dict = self.config["standards"]
        self.create_plot(target_dict=std_dict, savename="standards")

    def plot_targets(self):
        from betternot.fritz import radec

        target_dict = {}

        for ztf_id in self.ztf_ids:
            ra, dec = radec(ztf_id)
            if ra is None:
                self.logger.info(f"Source {ztf_id} not found on Fritz, skipping.")
            else:
                target_dict.update({ztf_id: {"ra": ra, "dec": dec}})

        self.create_plot(target_dict=target_dict, savename="targets")

    def create_plot(self, target_dict: dict, savename: str):
        target_list = list(target_dict)
        label_size = 14

        plt.figure(figsize=(width := 9, width / 1.61))
        ax = plt.subplot(111)

        midnight_utc = Time(self.date, format="isot", scale="utc") + (1 * u.hour)
        delta_midnight = np.linspace(-12, 12, 1000) * u.hour

        frame_time = AltAz(obstime=midnight_utc + delta_midnight, location=self.site)

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
            obj_airmass = obj_altazs.secz

            # moon_distance = check_moon(coords, midnight_utc, obs_NOT)

            mask = (obj_airmass > 0) & (obj_airmass < 5)

            ax.plot(
                delta_midnight,
                obj_altazs.alt,
                label=target,
                # label=f"{star} (moon distance: {sep:.0f}°)".format(
                # obj=star
                # ),  # , sep=moon_distance["sep"]
                # ),
                lw=2,
                # color=colors_vigit[2 * ii],
            )

        sunaltazs = get_body("sun", midnight_utc + delta_midnight).transform_to(
            frame_time
        )

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

        ax.set_title(
            self.date + " → " + (Time(self.date) + (1 * u.day)).isot.split("T")[0],
            fontsize=label_size,
        )

        plt.grid(True, color="gray", linestyle="dotted", which="both", alpha=0.5)
        plt.legend()

        outdir = get_date_dir(self.date)
        outpath = outdir / f"{savename}.pdf"

        plt.savefig(outpath, bbox_inches="tight")
        plt.close()

    @staticmethod
    def altitude_to_airmass(airmass):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            altitude = 1.0 / np.cos(np.radians(90 - airmass))
        return altitude

    @staticmethod
    def airmass_to_altitude(altitude):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            airmass = 90 - np.degrees(np.arccos(1 / altitude))
        return airmass
