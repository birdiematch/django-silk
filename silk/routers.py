# coding=utf-8
from silk.config import SilkyConfig
import logging

logger = logging.getLogger(__name__)


class SilkDBRouter:
    silk_database = SilkyConfig().SILKY_DATABASE_NAME
    logger.debug(f"Using silk_database '{silk_database}'")

    def db_for_read(self, model, **hints):
        if model._meta.app_label == "silk":
            return self.silk_database

        # No opinion
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == "silk":
            return self.silk_database

        # No opinion
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == obj2._meta.app_label == "silk":
            return True

        # No opinion
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):

        # Not a relevant app, no opinion
        if app_label != "silk":
            return None

        # Allow silk models only on specified database
        if db == self.silk_database:
            return True

        # Silk model on database that was not specified: disagree
        return False
