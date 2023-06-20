#!/usr/bin/env python3
# Author: Simeon Reusch (simeon.reusch@desy.de), most of the code is from Steve Schulze (steve.schulze@fysik.su.se)
# License: BSD-3-Clause

import datetime

import astroplan as ap  # type: ignore
import astropy  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import numpy as np
from astroplan.plots import plot_airmass, plot_altitude  # type: ignore
from astropy import units as u  # type: ignore
from astropy.coordinates import AltAz, EarthLocation, SkyCoord  # type: ignore
from astropy.time import Time  # type: ignore

from betternot.io import load_config


class Observability:
    def __init__(self, ztf_id, date: str | None = None):
        self.ztf_id = ztf_id
        if date is None:
            self.date = datetime.date.today().strftime("%Y-%m-%d")
        else:
            self.date = date
        self.site = ap.Observer.at_site(
            "Roque de los Muchachos", timezone="Europe/Berlin"
        )
        self.config = load_config()
        self.now = Time(datetime.datetime.utcnow())
        now_mjd = Time(self.now, format="iso").mjd

        # if self.date is not None:
        #     _date = self.date + " 12:00:00.000000"
        #     self.time_center = self._date
        # else:
        #     self.time_center = Time(now_mjd + 0.45, format="mjd").iso

        # # define an observability window
        # if self.date is not None:
        #     self.start_obswindow = Time(self.date + " 00:00:00.000000")
        # else:
        #     self.start_obswindow = Time(self.now, format="iso")

        # self.end_obswindow = Time(self.start_obswindow.mjd + 1, format="mjd").iso
        # self.times = Time(self.start_obswindow + np.linspace(0, 24, 1000) * u.hour)

        # self.get_twilight()
        # self.get_moon()

    # def get_twilight(self):
    #     self.twilight_evening = self.site.twilight_evening_astronomical(
    #         Time(self.start_obswindow), which="next"
    #     )
    #     self.twilight_morning = self.site.twilight_morning_astronomical(
    #         Time(self.start_obswindow), which="next"
    #     )

    # def get_moon(self):
    #     moon_times = Time(self.start_obswindow + np.linspace(0, 24, 200) * u.hour)
    #     self.moon = []

    #     for time in moon_times:
    #         moon_coord = astropy.coordinates.get_body(
    #             "moon", time=time, location=self.site.location
    #         )
    #         self.moon.append(moon_coord)

    def plot_standards(self):
        std_dict = self.config["standards"]
        std_list = list(std_dict)

        plt.figure(figsize=(9 * np.sqrt(2), 9))
        ax = plt.subplot(111)

        obs_NOT = EarthLocation.of_site("lapalma")

        midnight_utc = Time(self.date, format="isot", scale="utc") + 1
        delta_midnight = np.linspace(-12, 12, 1000) * u.hour

        frame_time = AltAz(obstime=midnight_utc + delta_midnight, location=obs_NOT)

        for star in std_list:
            coords = SkyCoord(
                std_dict[star]["ra"], std_dict[star]["dec"], unit=(u.hour, u.deg)
            )
            target = ap.FixedTarget(name=star, coord=coords)

            # ax = self.plot_target(target)
            obj_altazs = coords.transform_to(frame_time)
            obj_airmass = obj_altazs.secz

            # moon_distance = check_moon(coords, midnight_utc, obs_NOT)

            mask = (obj_airmass > 0) & (obj_airmass < 5)
            ax.plot(
                delta_midnight,
                obj_altazs.alt,
                label=star,
                # label=f"{star} (moon distance: {sep:.0f}°)".format(
                # obj=star
                # ),  # , sep=moon_distance["sep"]
                # ),
                lw=4,
                # color=colors_vigit[2 * ii],
            )

        # ax.axvspan(
        #     self.twilight_evening.plot_date,
        #     self.twilight_morning.plot_date,
        #     alpha=0.2,
        #     color="gray",
        # )

        # midnight = min(self.twilight_evening, self.twilight_morning) + 0.5 * (
        #     max(self.twilight_evening, self.twilight_morning)
        #     - min(self.twilight_evening, self.twilight_morning)
        # )

        # ax.annotate(
        #     "Night",
        #     xy=[midnight.plot_date, 85],
        #     color="dimgray",
        #     ha="center",
        #     fontsize=12,
        # )

        plt.legend()
        plt.savefig("test.pdf", bbox_inches="tight")

    def plot_target(self, target):
        ax = plot_altitude(
            target,
            self.site,
            self.time_center,
            min_altitude=10,
            style_kwargs={"fmt": "-"},
        )

        return ax
