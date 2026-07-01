from math import exp, pow, isinf, isnan

from src.utils import interpolation

base_curve = [[0.0, 0.0], [0.6, 0.256], [0.65, 0.296], [0.7, 0.345], [0.75, 0.404], [0.8, 0.473], [0.825, 0.522], [0.85, 0.581], [0.875, 0.65], [0.9, 0.729], [0.91, 0.768], [0.92, 0.813], [0.93, 0.867], [0.94, 0.931], [0.95, 1.0], [0.955, 1.039], [0.96, 1.094], [0.965, 1.167], [0.97, 1.256], [0.9725, 1.315], [0.975, 1.392], [0.9775, 1.49], [0.98, 1.618], [0.9825, 1.786], [0.985, 2.007], [0.9875, 2.303], [0.99, 2.7], [0.9925, 3.241], [0.995, 4.01], [0.9975, 5.158], [0.999, 6.241], [1.0, 7.424]]

def calculate_pp(acc_stars, pass_stars, tech_stars, acc):
    if not acc_stars or not pass_stars or not tech_stars:
        return 0

    pass_pp = 15.2 * exp(pow(pass_stars, 1 / 2.62)) - 30.0

    if isinf(pass_pp) or isnan(pass_pp) or pass_pp < 0:
        pass_pp = 0.0

    acc_pp = interpolation.interpolate(acc, base_curve) * acc_stars * 34.0
    tech_pp = exp(1.9 * acc/100) * 1.08 * tech_stars

    pp = 650.0 * pow(pass_pp + acc_pp + tech_pp, 1.3) / pow(650.0, 1.3)

    return pp

def convert_difficulty(difficulty):
    if difficulty == 1:
        return "Easy"
    elif difficulty == 3:
        return "Normal"
    elif difficulty == 5:
        return "Hard"
    elif difficulty == 7:
        return "Expert"
    elif difficulty == 9:
        return "ExpertPlus"
    else:
        return "Unknown"