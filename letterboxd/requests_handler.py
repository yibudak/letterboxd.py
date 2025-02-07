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
import requests

from .constants import API_HOSTNAME, USER_AGENT


class LetterboxdSession(requests.Session):
    def __init__(
        self,
        timeout: int = 15,
        verify: bool = True,
        proxy: dict[str:str] | None = None,
    ):
        super().__init__()
        self._base_url = f"https://{API_HOSTNAME}"
        self._timeout = timeout
        self._proxy = proxy
        self._verify = verify
        self.headers = {
            "User-Agent": USER_AGENT,
            "Accept-Encoding": "gzip",
        }

    def http(
        self,
        *args,
        **kwargs,
    ) -> requests.Response:
        url = self._base_url + kwargs.pop("path", "")
        with self as session:
            try:
                response = session.request(
                    *args,
                    **kwargs,
                    url=url,
                    timeout=self._timeout,
                    headers=self.headers,
                    proxies=self._proxy,
                    verify=self._verify,
                )
                # response.raise_for_status()
                return (
                    response.json()
                )  # Since API always returns JSON, we can return the JSON response
            except requests.exceptions.RequestException:
                # TODO: Log the error
                return requests.Response()
