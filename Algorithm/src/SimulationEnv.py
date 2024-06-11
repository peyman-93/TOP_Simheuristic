# -*- coding: utf-8 -*-


# Import libraries
import time
from FlexSimConnection import FlexSimConnection

# Parameters


# Classes    

class Simulation():
    """
    Class for creating a Simulation object

    To run the simulation, method run_simulation() has to be used
    
    """

    def __init__(self, param, Input_file, seed):

        self.p = param
        self.Input_file = Input_file
        self.seed = seed
    #    self.model_name = self.get_model_name()

  #  def get_model_name(self):
  #      if self.p.WH_TYPE in ["S", "M", "L"]:
  #          model_name = self.p.VER+"_"+self.p.WH_TYPE+".fsm"
  #      else:
  #          model_name = None

  #      return model_name

    def run_simulation(self):


        #abs_path = "C:/Users/jonas.fuentesleon/OneDrive - SPINDOX SPA/Documents/FlexSim 2022 Projects/2022_paper_SH/"
        #abs_path = "D:/wh_simu_code_20221008/"
        #abs_path = "C:/Users/Asus/Desktop/PhD_Works/2022_paper_work/flexsim_wsc/Warehouse_paper/wh_simu_code_20221008 (1)_finall/"
        #modelName = "C:/Users/Mohammad/Desktop/New Model/original-zones-connceted-jl2-3v.fsm"
        #modelName = "C:/Users/Mohammad/Desktop/New Model/original-zones-connceted-jl2-2v.fsm"
        #modelName = "C:/Users/Mohammad/Desktop/New Model/original-zones-connceted-2v-p6.fsm"
        modelName = "C:/Users/Mohammad/Desktop/New Model/original-zones-connceted-3v-p6.fsm"





        #order_file = abs_path+self.file_name
        #slots_file = order_file.replace("order", "slots")
        #modelName = self.p.VER+"_"+self.p.WH_TYPE+".fsm"
        Input_file = self.Input_file
        #Input_file = "LocationToGo.csv"
       
    
        FS = FlexSimConnection(
            flexsimPath="C:/Program Files/FlexSim 2023/program/flexsim.exe",
            modelPath = modelName,
            verbose=False,
            visible = False,
            #visible=self.p.VIS
        )
        # Launch:
        FS._launch_flexsim()
        start_time = time.time()

        # Set up simulation:
        # dummy message (required for communication sequence)
        FS._socket_send(str(1).encode())
        msg_recv = FS._socket_recv().decode('utf-8')
        FS._socket_send(str(Input_file).encode())
        msg_recv = FS._socket_recv().decode('utf-8')
        #FS._socket_send(str(slots_file).encode())
        #msg_recv = FS._socket_recv().decode('utf-8')
        FS._socket_send(str(self.p.SPEED).encode())
        msg_recv = FS._socket_recv().decode('utf-8')
        FS._socket_send(str(self.seed).encode())

        # Running simulation:
        done = False
        while not done:
            try:
                msg_recv = FS._socket_recv().decode('utf-8')
                done = self.respond_msg_recv(FS, msg_recv)

            except Exception as e:
                print(e)
                done = True
                FS._close_flexsim()

        # Close:
        end_time = time.time()
        elapsed_time = round(end_time - start_time, 2)
        print("simulation elapsed time: {}s".format(elapsed_time))
        FS._close_flexsim()

        return elapsed_time

    def respond_msg_recv(self, FS, msg_recv):
        """
        Function to select answer for each message from FlexSim
        """
        if msg_recv == "message1":
            FS._socket_send(str("answer1").encode())
        elif msg_recv == "message2":
            FS._socket_send(str("answer2").encode())
        elif msg_recv == "done":
            #print("end of simulation")
            done = True
        # TODO: case of unknown message
        # else:

        return done


"""


# Main execution:
if __name__ == "__main__":
    sim = Simulation()
    sim.run_simulation()

#    main()
"""

# Functions
def main():
    pass


# Main execution:
if __name__ == "__main__":
    main()