from http import cookies

from django.utils.deprecation import MiddlewareMixin

cookies.Morsel._flags.add("partitioned")  # type: ignore
cookies.Morsel._reserved.setdefault("partitioned", "Partitioned")  # type: ignore


class PartitionedCookieMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        cookies_to_modify = []
        for cookie in response.cookies.values():
            if (
                cookie.get("samesite") == "None"
                and cookie.get("secure")
                and cookie.get("httponly")
            ):
                cookies_to_modify.append(cookie)

        for cookie in cookies_to_modify:
            if "Partitioned" not in cookie:
                cookie["Partitioned"] = True

        return response
