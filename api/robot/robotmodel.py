import datetime

class RobotData:
    def __init__(self):
        self.root = "D:/gh-repo/lego-agent/api/temp"
        self.runid = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        self.field_data = {}

        self.sequence = 0

        # step 0
        self.step0_img_path = None

    # step 1
    def step1_analyze_img(self):
        return f"{self.root}/{self.runid}_step1_analyze_img.jpg"

    def step1_analyze_json(self):
        return f"{self.root}/{self.runid}_step1_analyze_json.json"

    def step1_analyze_json_data(self):
        with open(self.step1_analyze_json(), "r", encoding="utf-8") as file:
            contents = file.read()
        return contents

    # step 2
    def step2_plan_json(self):
        return f"{self.root}/{self.runid}_step2_plan_json.json"

    def step2_plan_json_data(self):
        with open(self.step2_plan_json(), "r", encoding="utf-8") as file:
            contents = file.read()
        return contents


class RoboProcessArgs:
    def __init__(self):
        self.image_path = "image_input.jpg"
        self.method = "color"
        self.templates = None
        self.target_objects = ["blue", "red"]
        self.confidence = 0.5
        self.output = "image_o.json"
        self.visualize = "image_v.json"
        self.pixels_per_unit = 1.0
        self.no_display = False
        self.no_preprocessing = False
