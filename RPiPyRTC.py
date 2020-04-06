#!/usr/bin/python

# RPiPyRTC - DS1307 RTC (Real Time Clock) Control
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

#/****************************************************************************/
#/* RPiPyRTC - Python DS1307 RTC (Real Time Clock) control application.      */
#/* ------------------------------------------------------------------------ */
#/* V1.00 - 2020-04-03 - Jason Birch                                         */
#/* ------------------------------------------------------------------------ */
#/* Application for controlling the DS1307 RTC via simulated I2C             */
#/* communication on the Raspberry Pi using Python.                          */
#/****************************************************************************/


import os
import sys
import time
import datetime
import RPi.GPIO
import RPiI2C


ARG_COUNT = 2
ARG_EXE = 0
ARG_SWITCH = 1
ARG_MESSAGE = 2


# DS1307 Constants.
DS1307_CTRL_OUT = 0x80
DS1307_CTRL_SQWE = 0x10
DS1307_CTRL_RATE_0 = 0x00
DS1307_CTRL_RATE_1 = 0x01
DS1307_CTRL_RATE_1HZ = 0x00
DS1307_CTRL_RATE_4KHZ = 0x01
DS1307_CTRL_RATE_8KHZ = 0x02
DS1307_CTRL_RATE_32KHZ = 0x03

DS1307_CTRL_BYTE = (DS1307_CTRL_OUT | DS1307_CTRL_SQWE | DS1307_CTRL_RATE_1HZ)

DOW = [ "",          "Sunday",   "Monday", "Tuesday", \
        "Wednesday", "Thursday", "Friday", "Saturday" ]

# I2C Command Data. To read specific register, write addres, then read data.
# WRITE: [READ_COUNT, [DS1307_ADDRESS + 0], REG_ADDRESS, DATA, DATA, ...]
# READ:  [READ_COUNT, [DS1307_ADDRESS + 1]]
DS1307_WRITE_ALL  = [0,  [0xD0, 0x00]]
DS1307_READ_ALL   = [64, [0xD1]]
DS1307_WRITE_TIME = [0,  [0xD0, 0x00]]
DS1307_READ_TIME  = [3,  [0xD1]]
DS1307_WRITE_DATE = [0,  [0xD0, 0x03]]
DS1307_READ_DATE  = [4,  [0xD1]]
DS1307_WRITE_CTRL = [0,  [0xD0, 0x07]]
DS1307_READ_CTRL  = [1,  [0xD1]]
DS1307_WRITE_MSG  = [0,  [0xD0, 0x08]]
DS1307_READ_MSG   = [56, [0xD1]]



#/*****************************************************/
#/* Display an array of data in ASCII and HEX format. */
#/*****************************************************/
def DisplayData(Data):
   for Byte in Data:
      if Byte >= 32 and Byte <= 127:
         sys.stdout.write(chr(Byte))
      else:
         sys.stdout.write(" {:02X} ".format(Byte))
   sys.stdout.write("\n")



if len(sys.argv) < ARG_COUNT:
   print(sys.argv[ARG_EXE] + " [-I|-S|-G|-M] [DATA]")
   print("WHERE:")
   print("-I - Initialise DS1307 device clock from system clock.")
   print("-S - Set the system clock from the DS1307 device clock.")
   print("-G - Read system clock, DS1307 device clock and message.")
   print("-M - Set DS1307 device message.")
else:
   # Initialise GPIO.
   RPi.GPIO.setwarnings(False)
   RPi.GPIO.setmode(RPi.GPIO.BCM)
   RPiI2C.I2C_Init()

   # Process command line arguments.
   if sys.argv[ARG_SWITCH][1] == 'I':
      # Initialise the DS1307 device.
      Now = time.gmtime(time.time())

      # Set the control byte to output a 1Hz signal on the output pin.
      SetData = list(DS1307_WRITE_CTRL[1])
      SetData.append(DS1307_CTRL_BYTE)
      RPiI2C.I2C_SendReceiveData(SetData)
      RPiI2C.I2C_SendReceiveData(DS1307_WRITE_CTRL[1])
#      Result = RPiI2C.I2C_SendReceiveData(DS1307_READ_CTRL[1], DS1307_READ_CTRL[0])
#      DisplayData(Result)

      # Set the DS1307 with the current system date.
      SetData = list(DS1307_WRITE_DATE[1])
      Day = Now.tm_wday + 2
      if Day > 7:
         Day = 1
      SetData.append(Day)
      SetData.append((Now.tm_mday % 10) + (int(Now.tm_mday / 10) << 4))
      SetData.append((Now.tm_mon % 10) + (int(Now.tm_mon / 10) << 4))
      SetData.append(((Now.tm_year - 2000) % 10) + (int((Now.tm_year - 2000) / 10) << 4))
      RPiI2C.I2C_SendReceiveData(SetData)

      # Set the DS1307 with the current system time.
      SetData = list(DS1307_WRITE_TIME[1])
      SetData.append((Now.tm_sec % 10) + (int(Now.tm_sec / 10) << 4))
      SetData.append((Now.tm_min % 10) + (int(Now.tm_min / 10) << 4))
      SetData.append((Now.tm_hour % 10) + (int(Now.tm_hour / 10) << 4))
      RPiI2C.I2C_SendReceiveData(SetData)

   elif sys.argv[ARG_SWITCH][1] == 'M':
      # Set the DS1307 message data.
      if len(sys.argv) > ARG_MESSAGE:
         SetData = list(DS1307_WRITE_MSG[1])
         for Char in sys.argv[ARG_MESSAGE]:
            SetData.append(ord(Char))
         for Count in range(56 - len(sys.argv[ARG_MESSAGE])):
            SetData.append(ord(' '))

         RPiI2C.I2C_SendReceiveData(SetData)
         RPiI2C.I2C_SendReceiveData(DS1307_WRITE_MSG[1])
         Result = RPiI2C.I2C_SendReceiveData(DS1307_READ_MSG[1], DS1307_READ_MSG[0])
         sys.stdout.write("DS1307 MESSAGE SET: ")
         DisplayData(Result)

   elif sys.argv[ARG_SWITCH][1] == 'S':
      # Set the system data and time from the DS1307 date, time.
      SetText = ""

      RPiI2C.I2C_SendReceiveData(DS1307_WRITE_DATE[1])
      Result = RPiI2C.I2C_SendReceiveData(DS1307_READ_DATE[1], DS1307_READ_DATE[0])
      SetText += "sudo date -s '20{:02X}-{:02X}-{:02X} ".format(Result[3], Result[2], Result[1])

      RPiI2C.I2C_SendReceiveData(DS1307_WRITE_TIME[1])
      Result = RPiI2C.I2C_SendReceiveData(DS1307_READ_TIME[1], DS1307_READ_TIME[0])
      SetText += "{:02X}:{:02X}:{:02X}'".format(Result[2], Result[1], Result[0])

      os.system(SetText)

   elif sys.argv[ARG_SWITCH][1] == 'G':
      # Display the system date and time, and the DS1307 date, time and message.
#      RPiI2C.I2C_SendReceiveData(DS1307_WRITE_ALL[1])
#      Result = RPiI2C.I2C_SendReceiveData(DS1307_READ_ALL[1], DS1307_READ_ALL[0])
#      sys.stdout.write("DS1307 ALL: ")
#      DisplayData(Result)

      # Display the time from the DS1307.
      RPiI2C.I2C_SendReceiveData(DS1307_WRITE_TIME[1])
      Result = RPiI2C.I2C_SendReceiveData(DS1307_READ_TIME[1], DS1307_READ_TIME[0])
      sys.stdout.write("DS1307 TIME: {:02X}:{:02X}:{:02X}\n".format(Result[2], Result[1], Result[0]))

      # Display the date from the DS1307.
      RPiI2C.I2C_SendReceiveData(DS1307_WRITE_DATE[1])
      Result = RPiI2C.I2C_SendReceiveData(DS1307_READ_DATE[1], DS1307_READ_DATE[0])
      sys.stdout.write("DS1307 DATE: {:s} 20{:02X}-{:02X}-{:02X}\n".format(DOW[Result[0]], Result[3], Result[2], Result[1]))

      # Display the message from the DS1307.
      RPiI2C.I2C_SendReceiveData(DS1307_WRITE_MSG[1])
      Result = RPiI2C.I2C_SendReceiveData(DS1307_READ_MSG[1], DS1307_READ_MSG[0])
      sys.stdout.write("DS1307 MESSAGE: ")
      DisplayData(Result)

      sys.stdout.write("\n")
      Now = datetime.datetime.now()
      # Display the system time.
      sys.stdout.write("SYSTEM TIME: {:s}\n".format(Now.strftime("%H:%M:%S")))

      # Display the system date.
      sys.stdout.write("SYSTEM DATE: {:s}\n".format(Now.strftime("%Y-%m-%d")))

