class ResponseHandling():
    def is_non_conforming_response(response):
        lines = response.splitlines()
        lines = [line.strip() for line in lines if line.strip()]
        has_sections = any(line.endswith(":") for line in lines)

        return not has_sections or len(lines) <= 1