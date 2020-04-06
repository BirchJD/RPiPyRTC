# Copyright (C) 2019 Jason Birch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.



Python DS1307 RTC (Real Time Clock) Control Application


Patreon, donations help produce more OpenSource projects:
https://www.patreon.com/_DevelopIT

Videos of this project:
https://youtu.be/rWAjvt1FGYg

Source Code on GitHub:
https://github.com/BirchJD/RPiPyRTC



Applications
============

./RPiPyRTC.py
Application for setting and viewing the system date and time, and the  DS1307
device date, time and message.

Use:
./RPiPyRTC.py [-I|-S|-G|-M] [DATA]
WHERE:
-I - Initialise DS1307 device clock from system clock.
-S - Set the system clock from the DS1307 device clock.
-G - Read system clock, DS1307 device clock and message.
-M - Set DS1307 device message with [DATA].


./RPiI2C.py
Python library for simulating I2C signals on two GPIO pins, to communicate with
I2C devices.



Circuit
=======

                             --------------
                            |              |
                            | Raspberry Pi |
                            |              |
                             --------------
                                  |  |
                               SDA|  |SCL
                                  |  |
     -------------------     --------------     -----------
    |                   |---|1    5  6    3|---| +         |
    | 32.768KHz Crystal |   |    DS1307    |   | 3V CR2032 |
    |                   |---|2  7      8  4|---| -         |
     -------------------     --------------  |  -----------
                                |      |     |
                                |      |     |
             |/|       ------   |      |     |
         ----| |------| 470R |--|------o     |
        |    |\|       ------   |      |     |
        |    LED                |      |     |
        |                       |      |     |
        |              ------   |      |     |
        |           --|  1K  |--       |     |
         \|        |   ------          |     |
          |--------|                   |     |
         /|BC337   |   ------          |     |
        |           --|  10K |---------o     |
        |              ------          |     |
        |                              |     |
        |                              ^     |
        |                              5V    |
        |                                    |
         ------------------------------------o
                                             |
                                             |
                                             v
                                             0V

