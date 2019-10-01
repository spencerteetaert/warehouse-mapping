import cProfile
pr = cProfile.Profile()
pr.enable()
import main
pr.disable()
pr.print_stats(sort='time')