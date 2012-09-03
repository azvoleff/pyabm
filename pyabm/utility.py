# Copyright 2011 Alex Zvoleff
#
# This file is part of the pyabm agent-based modeling toolkit.
# 
# pyabm is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
# 
# pyabm is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with
# pyabm.  If not, see <http://www.gnu.org/licenses/>.
#
# Contact Alex Zvoleff in the Department of Geography at San Diego State 
# University with any comments or questions. See the README.txt file for 
# contact information.

"""
Contains miscellaneous utility functions useful in building and running 
agent-based models.
"""

import logging
import smtplib
from email.MIMEText import MIMEText
from email.mime.multipart import MIMEMultipart

import numpy as np

from pyabm import rc_params
rcParams = rc_params.get_params()

logger = logging.getLogger(__name__)

class TimeSteps():
    def __init__(self, bounds, timestep):
        self._starttime = bounds[0]
        self._endtime = bounds[1]
        self._timestep = timestep

        # Initialize the current month and year
        self._year = self._starttime[0]
        self._month = self._starttime[1]
        self._int_timestep = 1

    def increment(self):
        self._month += self._timestep
        dyear = int((self._month - 1) / 12)
        self._year += dyear
        self._month = self._month - dyear*12
        self._int_timestep += 1
        assert self._month != 0, "Month cannot be 0"

    def in_bounds(self):
        if self._year == self._endtime[0] and self._month >= self._endtime[1] \
                or self._year > self._endtime[0]:
            return False
        else:
            return True

    def is_last_iteration(self):
        next_month = self._month + self._timestep
        dyear = int((next_month - 1) / 12)
        next_year = self._year + dyear
        next_month = next_month - dyear*12
        if next_year >= self._endtime[0] and next_month >= self._endtime[1]:
            return True
        else:
            return False
    
    def get_cur_month(self):
        return self._month

    def get_cur_year(self):
        return self._year

    def get_cur_date(self):
        return [self._year, self._month]

    def get_T0_date(self):
        """
        Returns the time one timestep prior to the starting time of the model 
        (T0).
        """
        T0_month = self._month - self._timestep
        dyear = int(1 - np.ceil(T0_month / 12.))
        T0_year = self._year - dyear
        T0_month = T0_month + dyear*12
        return [T0_year, T0_month]

    def get_cur_date_string(self):
        return "%.2d/%s"%(self._month, self._year)

    def get_T0_date_string(self):
        T0_year, T0_month = self.get_T0_date()
        return "%.2d/%s"%(T0_month, T0_year)

    def get_cur_date_float(self):
        return self._year + (self._month-1)/12.

    def get_T0_date_float(self):
        """
        Returns the time float one timestep prior to the starting time of the 
        model (T0).
        """
        T0_year, T0_month = self.get_T0_date()
        return T0_year + (T0_month-1)/12.

    def get_T_minus_date_float(self, neg_months):
        if neg_months > 0:
            raise Exception("Negative timestep must be provided to get_T_minus_date_float")
        T0_year, T0_month = self.get_T0_date()
        return T0_year + (T0_month+neg_months)/12.

    def get_cur_int_timestep(self):
        return self._int_timestep

    def __str__(self):
        return "%s-%s"%(self._year, self._month)

def email_logfile(log_file, subject='pyabm Log'):
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = rcParams['email_log.from']
    msg['To'] = rcParams['email_log.to']
    msg.preamble = 'This is a multi-part message in MIME format.'
    try:
        f = open(log_file, 'r')
    except IOError:
        logger.warning('Error reading logfile %s'%log_file)
        return 1
    file_content = f.read()
    f.close()
    # Include the log in the body of the email and as an attachment
    msg.attach(MIMEText(file_content, 'plain'))
    attachment = MIMEText(file_content, 'plain')
    attachment.add_header('Content-Disposition', 'attachment', filename=log_file)           
    msg.attach(attachment)
    try:
        server = smtplib.SMTP(rcParams['email_log.smtp_server'])
        server.login(rcParams['email_log.smtp_username'], rcParams['email_log.smtp_password'])
        server.sendmail(rcParams['email_log.from'], rcParams['email_log.to'], msg.as_string())
        server.quit()
    except smtplib.SMTPException:
        logger.warning('Error sending logfile %s via email. Check the email_log rcparams.'%log_file)
        return 1
    return 0
