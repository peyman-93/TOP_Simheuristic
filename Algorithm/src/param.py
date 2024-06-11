from datetime import datetime, date

class parameters:

    def __init__(self, review = True):


        self.ITER = 200  # number of iterations Metaheuristic > 0

        # FlexSim
        self.FS_SHORT_RUNS = 5   # number of runs for FlexSim for short simulation
        self.FS_LONG_RUNS = 10   # number of runs for FlexSim for long simulation
        #self.FS_RUNS = 10  # number of runs for FlexSim
        # Visible: opens FlexSim (True) or run in background (False)
        self.VIS = True # False -> run "fastforward"
        self.SPEED = 999  # Simulation speed (999 for "fastforward")
        
        self.review = review
        
        # Prepare parameters
        #self.initialize_param(self.review)

    def review_param(self):
        """
        Function to allow revision of the input parameters
        Pauses execution before full run
        """
        while True:
            # try:
            print("Please review parameters:\n")
            print(f"Num. Short FlexSim iterations: {self.FS_SHORT_RUNS}"+"\n" +
                  f"Num. Long FlexSim iterations: {self.FS_LONG_RUNS}" + "\n" +
                  f"FlexSim visibility: {self.VIS}")

            answer = input("Do you want to continue? type Y for yes\n > ")
            if answer == "Y":
                break
            raise Exception("Exit")
    
def main():
    p = parameters()
    p.review_param()
    #print("please run 'simu.py' instead")
    #
    # print(p.RACKS)
    

# Main execution:
if __name__ == "__main__":
    main()
