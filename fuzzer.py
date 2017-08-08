import socket
import select
import argparse

class fuzzy():

    def __init__(self):

        arguments = self.parse_arguments()
        technique = int(arguments.attack_technique)
        payloads = []

        if technique == 0:
            print "Sending original payloads only"
            payloads = self.send_original_payload(arguments.filename)
        elif technique == 1:
            print "Performing byte switcher technique"
            payloads = self.byte_switcher(arguments.filename)
        elif technique == 2:
            print "Performing length fuzzer technique"
            payloads = self.length_fuzzer(arguments.filename,pad_byte=int(arguments.pad_byte),maxlength=int(arguments.max_padding_length))

        i = 1
        for payload in payloads:
            print "---------------------Executing payload %d of %d---------------------" % (i,len(payloads))
            self.send_payload(payload,arguments.target,arguments.port,arguments.timeout,arguments.verbose)
            print "---------------------Finished payload %d of %d" % (i, len(payloads))
            i = i + 1

    def byte_switcher(self,filename):
        payloads = []

        bytes_arrays = self.generate_bytearray(filename)
        for bytes_array in bytes_arrays:
            for i in range(0,len(bytes_array)):
                for b in range(0,256):
                    modified_array = bytes_array[:]
                    modified_array[i] = chr(b)
                    payloads.append(modified_array)

        return payloads


    def length_fuzzer(self, filename,pad_byte=65,maxlength=100,step=10):
        payloads = []
        byte_arrays = self.generate_bytearray(filename)

        padding = bytearray(step)

        for i in range(0, step):
            padding[i] = pad_byte

        for bytes_array in byte_arrays:
            while len(bytes_array) < maxlength:
                bytes_array = bytes_array + padding
                payloads.append(bytes_array)
        return payloads

    def generate_bytearray(self,filename):
        bytearrays = []
        with open(filename) as f:
            content = f.readlines()

        lines = [x.strip() for x in content]

        for line in lines:
            arr = line.split(" ")
            bytearrays.append(bytearray(int(x, 16) for x in arr))

        return bytearrays

    #only send original payload from input file (no modification)
    def send_original_payload(self,filename):
        return self.generate_bytearray(filename)


    #this is ugly as code can be but i dont care
    def print_payload(self,byte_array):
        output = ""
        for i in range(0, len(byte_array)):
            if i > 0 and i % 4 == 0:
                temp_array = byte_array[i - 4:i]
                for j in range(0, len(temp_array)):
                    if temp_array[j] < 32 or temp_array[j] > 126:
                        # ascii of .
                        temp_array[j] = 46
                output += " " + temp_array + "\r\n"
            output += hex(byte_array[i]) + " "

            # end of array requires special case
            if i == (len(byte_array) - 1):

                left = (i % 4) + 1
                offset = len(byte_array) - left
                temp_array = byte_array[offset:]
                for j in range(0, len(temp_array)):
                    if temp_array[j] < 32 or temp_array[j] > 126:
                        # ascii of .
                        temp_array[j] = 46
                output += " " + temp_array + "\r\n"

        print output

    def send_payload(self,payload,target,port,timeout,verbose):

        Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        Socket.connect((target,int(port)))
        Socket.setblocking(0)
        if verbose:
            self.print_payload(payload)

        Socket.send(payload)

        # this prevents blocking when no response is set
        ready = select.select([Socket], [], [], float(timeout))
        if ready[0]:
            data = Socket.recv(4096)
            print data
            Socket.close()
        print "No Response"
        return






    def parse_arguments(self):
        parser = argparse.ArgumentParser(description='Parse')
        parser.add_argument("-t", "--target", help="Target host address", required=True)
        parser.add_argument("-p", "--port", help="Target port")
        parser.add_argument("-u", "--timeout", help="Timeout in seconds",default=1)
        parser.add_argument("-f", "--filename", help="Input file", default=1)
        parser.add_argument("-a", "--attack_technique", help="Attack techniques types: 0 = original payloads only, 1 = byte switch, 2 = length fuzzer", default=0)
        parser.add_argument("-v", "--verbose",help="set verbosity", action='store_true')
        parser.add_argument("-b", "--pad_byte", help="fuzz using this pad byte", default=65)
        parser.add_argument("-m", "--max_padding_length", help="max size for length fuzz", default=1000)
        arguments = parser.parse_args()


        if arguments.verbose:
            print arguments

        return arguments


if __name__ == '__main__':
    fuzzy = fuzzy()
