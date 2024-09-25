from website import create_app
import pprint


app = create_app()




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='8080')



    