class ProxyFix:
    def __init__(self, app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1):
        self.app = app
        self.x_for = x_for
        self.x_proto = x_proto
        self.x_host = x_host
        self.x_port = x_port
        self.x_prefix = x_prefix

    def __call__(self, environ, start_response):
        # X-Forwarded-For
        if self.x_for:
            real_ip = environ.get("HTTP_X_FORWARDED_FOR")
            if real_ip:
                if "," in real_ip:
                    real_ip = real_ip.split(",")[0].strip()
                environ["REMOTE_ADDR"] = real_ip

        # X-Forwarded-Proto
        if self.x_proto:
            proto = environ.get("HTTP_X_FORWARDED_PROTO")
            if proto:
                if "," in proto:
                    proto = proto.split(",")[0].strip()
                environ["wsgi.url_scheme"] = proto

        # X-Forwarded-Host
        if self.x_host:
            host = environ.get("HTTP_X_FORWARDED_HOST")
            if host:
                if "," in host:
                    host = host.split(",")[0].strip()
                environ["HTTP_HOST"] = host

        # X-Forwarded-Port
        if self.x_port:
            port = environ.get("HTTP_X_FORWARDED_PORT")
            if port:
                if "," in port:
                    port = port.split(",")[0].strip()
                environ["SERVER_PORT"] = port

        # X-Forwarded-Prefix
        if self.x_prefix:
            prefix = environ.get("HTTP_X_FORWARDED_PREFIX")
            if prefix:
                if "," in prefix:
                    prefix = prefix.split(",")[0].strip()
                environ["SCRIPT_NAME"] = prefix
                path_info = environ.get("PATH_INFO", "")
                if path_info.startswith(prefix):
                    environ["PATH_INFO"] = path_info[len(prefix):]

        return self.app(environ, start_response)