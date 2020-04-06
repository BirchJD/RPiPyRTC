# RPiI2C - I2C Communication for Raspberry Pi in Python
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
#/* PiI2C - I2C Communication for Raspberry Pi in Python.                    */
#/* ------------------------------------------------------------------------ */
#/* V1.00 - 2020-04-03 - Jason Birch                                         */
#/* ------------------------------------------------------------------------ */
#/* Library for I2C communication on the Raspberry Pi using Python.          */
#/****************************************************************************/


import sys
import time
import RPi.GPIO


# Define GPIO pin allocation.
GPIO_I2C_SDA = 2
GPIO_I2C_SCL = 3

# Fastest clock period for I2C. I2C supports slow 100KHz or fast 400KHz mode.
I2C_CLOCK_PERIOD = 0.000005
I2C_WORD_BITS = 8



#/************************/
#/* Initialise I2C GPIO. */
#/************************/
def I2C_Init():
   RPi.GPIO.setup(GPIO_I2C_SDA, RPi.GPIO.OUT, initial=1)
   RPi.GPIO.setup(GPIO_I2C_SCL, RPi.GPIO.OUT, initial=1)



#/*******************************/
#/* Signal start communication. */
#/*******************************/
def I2C_StartCom():
   RPi.GPIO.setup(GPIO_I2C_SDA, RPi.GPIO.OUT)
   RPi.GPIO.output(GPIO_I2C_SDA, 0)
   time.sleep(I2C_CLOCK_PERIOD)
   RPi.GPIO.output(GPIO_I2C_SCL, 0)
   time.sleep(I2C_CLOCK_PERIOD)



#/*****************************/
#/* Signal end communication. */
#/*****************************/
def I2C_EndCom():
   RPi.GPIO.setup(GPIO_I2C_SDA, RPi.GPIO.OUT)
   time.sleep(I2C_CLOCK_PERIOD)
   RPi.GPIO.output(GPIO_I2C_SCL, 1)
   time.sleep(I2C_CLOCK_PERIOD)
   RPi.GPIO.output(GPIO_I2C_SDA, 1)



#/*************************/
#/* Read ackknoledge bit. */
#/*************************/
def I2C_ReadAck():
   RPi.GPIO.setup(GPIO_I2C_SDA, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP)
   RPi.GPIO.output(GPIO_I2C_SCL, 1)
   time.sleep(I2C_CLOCK_PERIOD)
   Ack = RPi.GPIO.input(GPIO_I2C_SDA)
   RPi.GPIO.output(GPIO_I2C_SCL, 0)
   time.sleep(I2C_CLOCK_PERIOD)
   RPi.GPIO.setup(GPIO_I2C_SDA, RPi.GPIO.OUT)

   return Ack



#/*************************/
#/* Write ackknoledge bit. */
#/*************************/
def I2C_WriteAck(DataEndFlag):
   RPi.GPIO.setup(GPIO_I2C_SDA, RPi.GPIO.OUT)
   if DataEndFlag == False:
      RPi.GPIO.output(GPIO_I2C_SDA, 0)
   else:
      RPi.GPIO.output(GPIO_I2C_SDA, 1)
   RPi.GPIO.output(GPIO_I2C_SCL, 1)
   time.sleep(I2C_CLOCK_PERIOD)
   RPi.GPIO.output(GPIO_I2C_SCL, 0)
   time.sleep(I2C_CLOCK_PERIOD)
   RPi.GPIO.setup(GPIO_I2C_SDA, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP)



#/*****************************/
#/* Send data on the I2C bus. */
#/*****************************/
def I2C_SendReceiveData(Data, ReadByteCount = 0):
   ReceiveData = []

   I2C_StartCom()

   for DataWord in Data:
      BitMask = (1 << (I2C_WORD_BITS - 1))
      for Count in range(I2C_WORD_BITS):
         if (DataWord & BitMask) == 0:
            RPi.GPIO.output(GPIO_I2C_SDA, 0)
         else:
            RPi.GPIO.output(GPIO_I2C_SDA, 1)
         BitMask = BitMask / 2

         RPi.GPIO.output(GPIO_I2C_SCL, 1)
         time.sleep(I2C_CLOCK_PERIOD)
         RPi.GPIO.output(GPIO_I2C_SCL, 0)
         time.sleep(I2C_CLOCK_PERIOD)

      Ack = I2C_ReadAck()
#      print("DATA OUT: {:02X} ACK: {:02X}".format(DataWord, Ack))

   for ReadDataCount in range(ReadByteCount): 
      RPi.GPIO.setup(GPIO_I2C_SDA, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP)
      DataWord = 0
      for Count in range(I2C_WORD_BITS):
         RPi.GPIO.output(GPIO_I2C_SCL, 1)
         time.sleep(I2C_CLOCK_PERIOD)

         I2C_ReadBit = RPi.GPIO.input(GPIO_I2C_SDA)
         DataWord = DataWord * 2 + I2C_ReadBit

         RPi.GPIO.output(GPIO_I2C_SCL, 0)
         time.sleep(I2C_CLOCK_PERIOD)

      Ack = ((ReadDataCount + 1) == ReadByteCount)
      I2C_WriteAck(Ack)
#      print("DATA IN: {:02X} ACK: {:02X}".format(DataWord, Ack))

      ReceiveData.append(DataWord)

   I2C_EndCom()

   return ReceiveData

