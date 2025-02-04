# Copyright (c) 2025 Ahmet Yiğit Budak (https://github.com/yibudak)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
from base64 import b64decode

APP_VERSION = "2.19.4"
APP_VERSION_CODE = 365
API_HOSTNAME = "api.letterboxd.com"
CLIENT_ID = "48794061-18e9-a49d-d63c-ee625dad8131"
CLIENT_SECRET_ENCODED = (
    "ZTJlZGM1MGJkMDF",
    "lNjdkZmUxMzQ5ZW",
    "I2YjRmOWRhOWE3M",
    "DYzY2Q5MzA0NWNm",
    "Njg3MTYyMDYwZWZ",
    "iMDY2NDllZg==",
)
CLIENT_SECRET = b64decode("".join(CLIENT_SECRET_ENCODED)).decode("utf-8")
USER_AGENT = (
    f"Letterboxd Android {APP_VERSION} ({APP_VERSION_CODE}) / Android 30 Redmi Note 9"
)
