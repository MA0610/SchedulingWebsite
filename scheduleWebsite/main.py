from website import create_app
import pprint


app = create_app()

if __name__ == '__main__':
     app.run(debug=True)



###################################
#maybe try out numpy maybe to make this easier if needed


#Monday has total of 20 possible slots
#Tuesday has a total of 11 possible slots

#M-F class sets (0)
#8:30-9:25 am
#1:55-2:50 pm

#MWF class sets (1)
#8:30-9:25 am
#9:35-10:30 am
#10:40-11:35 am
#11:45-12:40 pm
#1:55-2:50 pm
#3:00-3:55 pm
#4:05-5:00 pm

#TR class sets (2)
#8:30-9:55 am
#10:05-11:30 am
#1:30-2:55 pm
#3:05-4:30 pm
#5:00-6:25 pm

#MW class sets (3)
#8:00-9:25 am
#4:05-5:30 pm
#5:40-7:05 pm
#7:15-8:40 pm
#8:50-10:15 pm

#MF class sets (4)
#8:00-9:25 am
#4:05-5:30 pm

#MW class sets (5)
#8:00-9:25 am
#4:05-5:30 pm

#T OR R class sets (6)
#1:30-4:25 pm
#8:30-11:25 am
#1:30-4:25 pm


#T OR W OR R class sets (7)
#7:15-10:15 pm


###############
#LABS

#T OR R class sets (8)
#8:30-11:25 am
#1:30-4:25 pm

#W OR F (9)
#1:55-4:50 pm

#M OR W (10)
#3:00-5:55 pm

#M OR W OR R (11)
#7:15-10:10 pm


#may have key for num of rows if there isn't flexibility in times during day
#(ex. TR 10:05-11:30 is traditional but can profs make a time slot of 9:45-11:10)

#x is num of rows (time slots on given day: ?)
#y is num of columns (number of days in week: 5)
#z is num of entries in array (lists: 1)
def create_3d_list(x,y,z):
    lst = []
    for i in range(x):
        lst_2d = []
        for j in range(y):
            lst_1d = []
            for k in range(z):
                lst_1d.append([])
            lst_2d.append(lst_1d)
        lst.append(lst_2d)
    return lst


test = create_3d_list(3, 5, 1)

test[0][0][0].append("3")
test[0][0][0].append("4")


##





# used the pretty printed function
pprint.pprint(test)





    
