import os


class Config(object):
    SECRET_KEY = "abacd74f966611e5a00240f02fd6707c"
    BOOTSTRAP_SERVE_LOCAL = True
    PER_PAGE = 10
    WTF_CSRF_ENABLED = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MONGODB_SETTINGS = {
        "DB": "dev-show"
    }


class ProductionConfig(Config):
    MONGODB_SETTINGS = {
        "DB": "thu-show"
    }


config = {
    "develop": DevelopmentConfig,
    "product": ProductionConfig,
    "default": DevelopmentConfig
}
