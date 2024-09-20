from website import create_app
import pprint


app = create_app()

# if __name__ == '__main__':
#     app.run(debug=True)



###################################
#maybe try out numpy maybe to make this easier if needed


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


#########
#





# used the pretty printed function
pprint.pprint(test)





    