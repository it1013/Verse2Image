import configparser
from pathlib import Path


class Config:
    def __init__(self, config_file="config.ini"):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

    # PATHS
    @property
    def epub_path(self):
        return self.config["PATHS"]["epub_path"]

    @property
    def output_dir(self):
        return self.config["PATHS"]["output_dir"]

    # IMAGE
    @property
    def img_width(self):
        return self.config.getint("IMAGE", "width")

    @property
    def img_height(self):
        return self.config.getint("IMAGE", "height")

    @property
    def margin_x(self):
        return self.config.getint("IMAGE", "margin_x")

    @property
    def margin_top(self):
        return self.config.getint("IMAGE", "margin_top")

    @property
    def margin_bot(self):
        return self.config.getint("IMAGE", "margin_bot")

    # COLORS
    @property
    def bg_color(self):
        return self.config["COLORS"]["bg_color"]

    @property
    def text_color(self):
        return self.config["COLORS"]["text_color"]

    @property
    def verse_num_color(self):
        return self.config["COLORS"]["verse_num_color"]

    @property
    def citation_color(self):
        return self.config["COLORS"]["citation_color"]

    @property
    def shadow_color(self):
        return self.config["COLORS"]["shadow_color"]

    # SIZING
    @property
    def end_block(self):
        return self.config["SIZING"]["end_block"]

    @property
    def max_lines(self):
        return self.config.getint("SIZING", "max_lines")

    @property
    def line_length(self):
        return self.config.getint("SIZING", "line_length")

    @property
    def font_size_max(self):
        return self.config.getint("SIZING", "font_size_max")

    @property
    def font_size_start(self):
        return self.config.getint("SIZING", "font_size_start")

    @property
    def font_size_min(self):
        return self.config.getint("SIZING", "font_size_min")

    @property
    def font_size_step(self):
        return self.config.getint("SIZING", "font_size_step")

    @property
    def citation_font_size(self):
        return self.config.getint("SIZING", "citation_font_size")

    @property
    def citation_x(self):
        return self.config.getint("SIZING", "citation_x")

    @property
    def citation_y(self):
        return self.config.getint("SIZING", "citation_y")

    @property
    def citation_x_offset(self):
        return self.config.getint("SIZING", "citation_x_offset")

    @property
    def citation_y_offset(self):
        return self.config.getint("SIZING", "citation_y_offset")

    @property
    def shadow_x_offset(self):
        return self.config.getint("SIZING", "shadow_x_offset")

    @property
    def shadow_y_offset(self):
        return self.config.getint("SIZING", "shadow_y_offset")

    @property
    def line_spacing(self):
        return self.config.getfloat("SIZING", "line_spacing")

    @property
    def centered(self):
        return self.config.getboolean("SIZING", "centered")

    # FONTS
    @property
    def font_candidates(self):
        return [
            line.strip()
            for line in self.config["FONTS"]["font_candidates"].splitlines()
            if line.strip()
        ]