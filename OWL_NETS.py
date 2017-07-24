#################################################
# OWL_NETS.py
# Purpose: primary script for OWL-NETS method
# version 1.2.2
# date: 07.20.2017
###############################################


## import module/script dependencies
import argparse
import tkFileDialog
from Tkinter import *
import tkMessageBox
import NETSRepresentation
import OWLRepresentation



class ProgramGUI:
    def __init__(self, master):
        self.master = master
        master.title("OWL-NETS") # window title

        self.label = Label(master, text='\n' + 'OWL-NETS: NEtwork Entity Transformation for Statistical Learning' + '\n') #
        self.label.grid(row = 0, columnspan = 3, sticky=N+W)

        # buttons
        self.button_go= Button(master, text="Go", command=self.ButtonGoCall)
        self.button_go.grid(row=1, column=0)

        self.browse_button = Button(master, text="Browse", command=self.ButtonBrowseCall)
        self.browse_button.grid(row=1, column=1)

        self.close_button = Button(master, text="Exit", command=master.quit)
        self.close_button.grid(row=1, column=2)

        # check-box
        self.var1 = IntVar()
        self.check1 = Checkbutton(master, text="OWL-NETS Network", variable=self.var1, command = self.Checkbutton1)
        self.check1.grid(row=3, column = 0)

        self.var2 = IntVar()
        self.check2 = Checkbutton(master, text="OWL Network      ", variable=self.var2, command=self.Checkbutton2)
        self.check2.grid(row=3, column=2)

        # value entry
        self.entry = Entry(master, width=50)
        self.entry.grid(row = 2, columnspan = 3, sticky=N+W)

        # add message to bottom of window
        self.statusText = StringVar(master)
        self.statusText.set('\n' + 'To get started, please press Browse or enter the path/name to your query, '
                            'choose which kind of network you would like to build, then press Go' + '\n')

        self.message = Label(master, textvariable=self.statusText, wraplength=375, justify = CENTER)
        self.message.grid(row = 5, columnspan = 3)


    # define button functionality
    def ButtonGoCall(self):
        '''Function stores the functionality for the 'GO' button '''
        val_check = self.Validate()  # check to make sure that input was provided
        if val_check != 0: # if func is correct return 0
            return

        input_file = self.entry.get()
        # output = self.GetOutputName(input_file)

        # run program
        if self.Checkbutton1() == 1:
            NETSRepresentation.NETSNetworkBuilder(input_file)

        if self.Checkbutton2() == 1:
            OWLRepresentation.OWLNetworkBuilder(input_file)

        self.Complete()


    def ButtonBrowseCall(self):
        '''Function stores the functionality for the 'Browse' button '''
        filename = tkFileDialog.askopenfilename()
        self.entry.delete(0, END)
        self.entry.insert(0, filename)

    def Checkbutton1(self):
        '''Function stores the functionality for the NETS network checkbutton'''
        if (self.var1.get()):
            return 1

    def Checkbutton2(self):
        '''Function stores the functionality for the OWL network checkbutton'''
        if (self.var2.get()):
            return 1


    def Validate(self):

        if self.Checkbutton1() != 1 and self.Checkbutton2() != 1:
            tkMessageBox.showwarning("Error", "Please select your file and indicate the type of network to build")
            return 99
        return 0 # means there is no error

    def Complete(self):
        tkMessageBox.showinfo("Program Finished", "Program is complete, you can find your files are in the same "
                                                  "directory as your query")
        root.quit()
        return


def InputParser():
    ''' Function parses the input information if the user chooses to run the program via the command line '''

    parser = argparse.ArgumentParser(
        description='OWL-NETS: NEtwork Entity Transformation for Statistical Learning. For program to run correctly the '
                    'input arguments must be formatted as shown below.')
    parser.add_argument('-a', '--input', help='name/path to SPARQL query file (e.g., Folder/Query1_query)')
    parser.add_argument('-b', '--owl', help='type "owl" to generate OWL representation')
    parser.add_argument('-c', '--nets', help='type "owl-nets" to generate OWL-NETS representation')
    parser.add_argument('-d', '--both', help='type "both" to generate both representations')


    return parser


def CommandLine(args):
    '''Function stores the information needed to execute the program via the command line '''

    # runs only OWL-NETS
    if args.nets == 'owl-nets' and args.owl != 'owl':
        NETSRepresentation.NETSNetworkBuilder(args.input)

    # runs only OWL
    if args.owl == 'owl' and args.nets != 'owl-nets':
        OWLRepresentation.OWLNetworkBuilder(args.input)

    # runs both OWL-NETS and OWL
    if args.both == 'both':
        NETSRepresentation.NETSNetworkBuilder(args.input)
        OWLRepresentation.OWLNetworkBuilder(args.input)



    print "Program is complete!"



if __name__ == "__main__":

    parser = InputParser()          # start the command-line argument parsing
    args = parser.parse_args()      # read the command-line arguments

    if args.input:                  # If there is an argument, run the command-line version
        CommandLine(args)
    else:
        root = Tk()
        root.lift()
        root.attributes('-topmost', True)
        my_gui = ProgramGUI(root)
        root.mainloop()