import os

from configs.conf import MODEL_BASE_DIR
from tools.data.path_hdl import directory_ensure


class Model:
    def __init__(self):
        self.name = None
        self.dependency = None
        self.path = None
        self.description = None

    def __str__(self):
        pass

    def __del__(self):
        pass

    def model_init(self, name):
        self.path = os.path.join(MODEL_BASE_DIR, name)
        if self.model_exists():
            self.model_file_structure_check()
        else:
            directory_ensure(os.path.join(self.path, "ctrls"))
            directory_ensure(os.path.join(self.path, "pythons"))
            directory_ensure(os.path.join(self.path, "scripts"))

    def model_delete(self):
        pass

    def load_info(self):
        pass

    def save_info(self):
        pass

    def dependency_analysis(self):
        pass

    def model_exists(self):
        pass

    def model_file_structure_check(self):
        pass


class ModelManager:
    def __init__(self):
        self.model_base_dir = MODEL_BASE_DIR
        self.model_list = []
        self.work_flow = None
        self.scheduled_jobs = []

    def __str__(self):
        pass
