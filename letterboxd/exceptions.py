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
import json


class LetterboxdError(Exception):
    """Base class for other exceptions"""

    def __init__(self, response: dict):
        self.message = json.dumps(response, indent=4)
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"Letterboxd Error: {self.message}"


class AuthenticationError(LetterboxdError):
    """Raised when authentication failed"""

    def __str__(self) -> str:
        return f"Authentication Error: {self.message}"


class MemberNotFoundError(LetterboxdError):
    """Raised when member not found"""

    def __str__(self) -> str:
        return f"Member Not Found: {self.message}"


class TooManyFollow(LetterboxdError):
    """Raised when trying to follow too many members in a day, 500 is the limit."""

    def __str__(self) -> str:
        return f"Too Many Follow: {self.message}"


class InvalidRatingError(LetterboxdError):
    """Raised when an invalid rating is given"""

    def __str__(self) -> str:
        return f"Invalid Rating: {self.message}"


class UnknownError(LetterboxdError):
    """Raised when an unknown error occurred"""

    def __str__(self) -> str:
        return f"Unknown Error: {self.message}"
