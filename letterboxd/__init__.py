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
from datetime import datetime, timedelta

from .requests_handler import LetterboxdSession

from . import exceptions
from .constants import CLIENT_ID, CLIENT_SECRET


class Letterboxd:
    def __init__(
        self,
        username: str,
        password: str,
        reconnect: bool = True,
        log_level: str = "INFO",
    ):
        self.__username = username
        self.__password = password
        self.__auth_token = None
        self.__session = LetterboxdSession(
            # TODO: Add timeout, verify, proxy
        )
        self.reconnect = reconnect
        self.logged_in = False
        self.session_expire_date = None
        
    def login(self):
        self._login()
        self.member_id = self.get_me()["member"]["id"]

    def _login(self) -> bool:
        response = self.__session.http(
            method="POST",
            path="/api/v0/auth/token",
            data={
                "grant_type": "password",
                "username": self.__username,
                "password": self.__password,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            },
        )
        self._handle_error(response)

        self.__auth_token = f"Bearer {response['access_token']}"
        self.__logged_in = True
        self._set_session_expire_date(response["expires_in"])
        self.__session.headers.update({"Authorization": self.__auth_token})

        return True

    def _set_session_expire_date(self, expires_in: int):
        self.session_expire_date = datetime.now() + timedelta(seconds=expires_in)

    def _handle_error(self, response: dict) -> None:
        response_str = str(response)
        if not response.get("error") and "Error" not in response_str:
            return

        if response.get("message") == "Member not found":
            raise exceptions.MemberNotFoundError(response)

        elif "Too many follows." in response_str:
            raise exceptions.TooManyFollow(response)

        raise exceptions.UnknownError(response)

    ### Follow/Unfollow ###

    def _set_user_follow(self, user_id: str, action: str) -> bool:
        return self.__session.http(
            method="PATCH",
            path=f"/api/v0/member/{user_id}/me",
            json={
                "following": True if action == "follow" else False,
            },
        )

    def follow_user(self, user_id: str):
        response = self._set_user_follow(user_id, "follow")
        self._handle_error(response)
        following_status = response["data"]["following"]  # Should be True
        return following_status

    def unfollow_user(self, user_id: str) -> bool:
        response = self._set_user_follow(user_id, "unfollow")
        self._handle_error(response)
        following_status = response["data"]["following"]  # Should be False
        return not following_status

    ### Getters ###

    def get_activities(
        self,
        member_id: str,
        per_page: int = 24,
        start: int = 1,
    ) -> dict:
        """
        TODO: currently it only returns DiaryEntryActivity. implement other activities
        later.
        """
        params = {
            "perPage": per_page,
            "include": "DiaryEntryActivity",
        }
        if start > 1:
            params["cursor"] = f"start={start}"
        response = self.__session.http(
            method="GET",
            path=f"/api/v0/member/{member_id}/activity",
            params=params,
        )
        self._handle_error(response)
        return response

    def get_news(self, per_page: int = 20, start: int = 1) -> dict:
        # Max 100 per page
        response = self.__session.http(
            method="GET",
            path="/api/v0/news",
            params={
                "perPage": per_page,
                "cursor": f"start={start}",
            },
        )
        self._handle_error(response)
        return response

    def get_me(self) -> dict:
        response = self.__session.http(
            method="GET",
            path="/api/v0/me",
        )
        self._handle_error(response)
        return response

    def get_user_me(self, user_id: str) -> dict:
        response = self.__session.http(
            method="GET",
            path=f"/api/v0/member/{user_id}/me",
        )
        self._handle_error(response)
        return response

    def get_member_stats(self, user_id: str) -> dict:
        response = self.__session.http(
            method="GET",
            path=f"/api/v0/member/{user_id}/statistics",
        )
        self._handle_error(response)
        return response

    def _get_following_status(
        self,
        user_id: str,
        per_page: int = 40,
        start: int = 1,
        sort: str = "Date",
        action: str = "following",
    ) -> dict:
        """
        Max: 100 per page
        Available sort options:
         - Date
         - Name
         - MemberPopularity
         - MemberPopularityThisWeek
         - MemberPopularityThisMonth
         - MemberPopularityThisYear
         - MemberPopularityWithFriends
         - MemberPopularityWithFriendsThisWeek
         - MemberPopularityWithFriendsThisMonth
         - MemberPopularityWithFriendsThisYear
        """
        params = {
            "perPage": per_page,
            "sort": sort,
            "member": user_id,
            "memberRelationship": "IsFollowing"
            if action == "following"
            else "IsFollowedBy",
        }
        if start > 1:
            params["cursor"] = f"start={start}"

        response = self.__session.http(
            method="GET",
            path="/api/v0/members",
            params=params,
        )
        self._handle_error(response)
        return response

    def get_followers(
        self,
        user_id: str,
        per_page: int = 40,
        start: int = 1,
        sort="Date",
    ) -> dict:
        return self._get_following_status(
            user_id=user_id,
            per_page=per_page,
            start=start,
            sort=sort,
            action="followers",
        )

    def get_followings(
        self,
        user_id: str,
        per_page: int = 40,
        start: int = 1,
        sort: str = "Date",
    ) -> dict:
        return self._get_following_status(
            user_id=user_id,
            per_page=per_page,
            start=start,
            sort=sort,
            action="following",
        )

    def get_film(self, film_id: str) -> dict:
        response = self.__session.http(
            method="GET",
            path=f"/api/v0/film/{film_id}",
        )
        self._handle_error(response)
        return response

    def get_film_members(
        self,
        film_id: str,
        sort: str = "Date",
        film_relationship: str = "Watched",
        start: int = 1,
    ) -> dict:
        """
        Available sort options:
            - All sorts from get_followers

        Available film_relationship options:
            - Watched (who watched the film)
            - Liked (who liked the film)
            - Favorited (who added the film to their favorites)


        """
        params = {
            "sort": sort,
            "filmRelationship": film_relationship,
        }
        if start > 1:
            params["cursor"] = f"start={start}"
        response = self.__session.http(
            method="GET",
            path=f"/api/v0/film/{film_id}/members",
            params=params,
        )
        self._handle_error(response)
        return response

    def get_film_statistics(self, film_id: str) -> dict:
        response = self.__session.http(
            method="GET",
            path=f"/api/v0/film/{film_id}/statistics",
        )
        self._handle_error(response)
        return response

    def get_film_me(self, film_id: str) -> dict:
        response = self.__session.http(
            method="GET",
            path=f"/api/v0/film/{film_id}/me",
        )
        self._handle_error(response)
        return response

    def get_film_availability(self, film_id: str) -> dict:
        response = self.__session.http(
            method="GET",
            path=f"/api/v0/film/{film_id}/availability",
        )
        self._handle_error(response)
        return response

    def get_log_entries(
        self,
        film_id: str,
        sort: str = "ReviewPopularity",
        where: str = "HasReview",
        start: int = 1,
    ) -> dict:
        """
        WTF YOU CAN GET ALL RECENT REVIEWS???
        Available sort options:
            - WhenAdded
            - ReviewPopularity

        Available where options:
            - HasReview
            - ???

        """
        params = {
            "film": film_id,
            "sort": sort,
            "where": where,
        }
        if start > 1:
            params["cursor"] = f"start={start}"
        response = self.__session.http(
            method="GET",
            path="/api/v0/log-entries",
            params=params,
        )
        self._handle_error(response)
        return response

    def get_log_entry_me(self, log_entry_id: str) -> dict:
        response = self.__session.http(
            method="GET",
            path=f"/api/v0/log-entry/{log_entry_id}/me",
        )
        self._handle_error(response)
        return response

    def get_log_entry(self, log_entry_id: str) -> dict:
        response = self.__session.http(
            method="GET",
            path=f"/api/v0/log-entry/{log_entry_id}",
        )
        self._handle_error(response)
        return response

    def get_films(
        self,
        sort: str = "FilmPopularity",
        start: int = 1,
        per_page: int = 20,
    ) -> dict:
        """
        Available sort options:
            - FilmPopularity
            - FilmPopularityThisWeek
            - FilmPopularityThisMonth
            - FilmPopularityThisYear
            - FilmPopularityWithFriends
            - FilmPopularityWithFriendsThisWeek
            - FilmPopularityWithFriendsThisMonth
            - FilmPopularityWithFriendsThisYear

        TODO: Add other filter options?
        """
        params = {
            "sort": sort,
            "perPage": per_page,
        }
        if start > 1:
            params["cursor"] = f"start={start}"
        response = self.__session.http(
            method="GET",
            path="/api/v0/films",
            params=params,
        )
        self._handle_error(response)
        return response

    ### Review Actions ###
    def _set_review_like(self, review_id: str, liked: bool) -> bool:
        response = self.__session.http(
            method="PATCH",
            path=f"/api/v0/log-entry/{review_id}/me",
            json={"liked": liked},
        )
        self._handle_error(response)
        return True

    def like_review(self, review_id: str) -> bool:
        response = self._set_review_like(review_id, liked=True)
        return response

    def unlike_review(self, review_id: str) -> bool:
        response = self._set_review_like(review_id, liked=False)
        return not response

    def send_review(
        self,
        film_id: str,
        review: str,
        rating: int,
        like: bool,
        diary_date: str = datetime.now().strftime("%Y-%m-%d"),
        rewatch: bool = False,
        contains_spoilers: bool = False,
        tags: list[str] = [],
    ) -> dict:
        data = {
            "filmId": film_id,
            "diaryDetails": {
                "diaryDate": diary_date,
                "rewatch": rewatch,
            },
            "review": {
                "text": review,
                "containsSpoilers": contains_spoilers,
            },
            "tags": tags,
            "rating": rating,
            "like": like,
        }
        response = self.__session.http(
            method="POST",
            path="/api/v0/log-entries",
            json=data,
        )
        self._handle_error(response)
        return response

    def delete_review(self, review_id: str) -> bool:
        response = self.__session.http(
            method="DELETE",
            path=f"/api/v0/log-entry/{review_id}",
        )
        self._handle_error(response)
        return True

    def watch_film(self, film_id: str) -> bool:
        response = self.__session.http(
            method="PATCH",
            path=f"/api/v0/film/{film_id}/me",
            json={"watched": True},
        )
        self._handle_error(response)
        return True

    def unwatch_film(self, film_id: str) -> bool:
        response = self.__session.http(
            method="PATCH",
            path=f"/api/v0/film/{film_id}/me",
            json={"watched": False},
        )
        self._handle_error(response)
        return True

    def rate_film(self, film_id: str, rating: int) -> bool:
        if rating > 5:
            raise exceptions.InvalidRatingError(rating)
        elif rating <= 0:
            rating = None
        response = self.__session.http(
            method="PATCH",
            path=f"/api/v0/film/{film_id}/me",
            json={"rating": rating},
        )
        self._handle_error(response)
        return True
