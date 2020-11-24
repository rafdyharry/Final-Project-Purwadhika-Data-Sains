# Flask : library utama untuk membuat API
# render_template : agar dapat memberikan respon file html
# request : untuk membaca data yang diterima saat request datang
from flask import Flask, render_template, request
# plotly dan plotly.graph_objs : membuat plot
import plotly
import plotly.graph_objs as go
# pandas : untuk membaca csv dan men-generate dataframe
import pandas as pd
import json
from sqlalchemy import create_engine

## Joblib untuk Load Model
import joblib

# untuk membuat route
app = Flask(__name__)

###################
## CATEGORY PLOT ##
###################

## IMPORT DATA USING pd.read_csv
# tips = pd.read_csv('./static/tips.csv')

# IMPORT DATA USING pd.read_sql
# sqlengine = create_engine('mysql+pymysql://kal:s3cret123@127.0.0.1/flaskapp', pool_recycle=3605)
# dbConnection = sqlengine.connect()
# engine = sqlengine.raw_connection()
# cursor = engine.cursor()
# tips = pd.read_sql("select * from tips", dbConnection)

# category plot function
def category_plot(
    cat_plot = 'histplot',
    cat_x = 'vehiclemodel', cat_y = 'ratedaily',
    estimator = 'count', hue = 'vehiclemake'):

    # generate dataframe tips.csv
    # tips = pd.read_csv('./static/tips.csv')



    # jika menu yang dipilih adalah histogram
    if cat_plot == 'histplot':
        # siapkan list kosong untuk menampung konfigurasi hist
        data = []
        # generate config histogram dengan mengatur sumbu x dan sumbu y
        for val in tips[hue].unique():
            hist = go.Histogram(
                x=tips[tips[hue]==val][cat_x],
                y=tips[tips[hue]==val][cat_y],
                histfunc=estimator,
                name=val
            )
            #masukkan ke dalam array
            data.append(hist)
        #tentukan title dari plot yang akan ditampilkan
        title='Histogram'
    elif cat_plot == 'boxplot':
        data = []

        for val in tips[hue].unique():
            box = go.Box(
                x=tips[tips[hue] == val][cat_x], #series
                y=tips[tips[hue] == val][cat_y],
                name = val
            )
            data.append(box)
        title='Box'
    # menyiapkan config layout tempat plot akan ditampilkan
    # menentukan nama sumbu x dan sumbu y
    if cat_plot == 'histplot':
        layout = go.Layout(
            title=title,
            xaxis=dict(title=cat_x),
            yaxis=dict(title='person'),
            # boxmode group digunakan berfungsi untuk mengelompokkan box berdasarkan hue
            boxmode = 'group'
        )
    else:
        layout = go.Layout(
            title=title,
            xaxis=dict(title=cat_x),
            yaxis=dict(title=cat_y),
            # boxmode group digunakan berfungsi untuk mengelompokkan box berdasarkan hue
            boxmode = 'group'
        )
    #simpan config plot dan layout pada dictionary
    result = {'data': data, 'layout': layout}

    #json.dumps akan mengenerate plot dan menyimpan hasilnya pada graphjson
    graphJSON = json.dumps(result, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

# akses halaman menuju route '/' untuk men-test
# apakah API sudah running atau belum
@app.route('/')
def index():

    plot = category_plot()
    # dropdown menu
    # kita lihat pada halaman dashboard terdapat menu dropdown
    # terdapat lima menu dropdown, sehingga kita mengirimkan kelima variable di bawah ini
    # kita mengirimnya dalam bentuk list agar mudah mengolahnya di halaman html menggunakan looping
    list_plot = [('histplot', 'Histogram'), ('boxplot', 'Box')]
    list_x = [('vehiclemodel', 'Vehicle Model'), ('vehicletype', 'Vehicle Type'), ('locationstate', 'Location State'), ('vehicletype', 'Vehicle Type')]
    list_y = [('rating', 'Rating'), ('vehicleyear', 'Vehicle Year'), ('ratedaily', 'Rate Daily')]
    list_est = [('count', 'Count'), ('avg', 'Average'), ('max', 'Max'), ('min', 'Min')]
    list_hue = [('(vehiclemodel', 'Vehicle Model'), ('vehicletype', 'Vehicle Type'), ('locationstate', 'Location State'), ('vehicletype', 'Vehicle Type')]

    return render_template(
        # file yang akan menjadi response dari API
        'category.html',
        # plot yang akan ditampilkan
        plot=plot,
        # menu yang akan tampil di dropdown 'Jenis Plot'
        focus_plot='histplot',
        # menu yang akan muncul di dropdown 'sumbu X'
        focus_x='vehiclemodel',

        # untuk sumbu Y tidak ada, nantinya menu dropdown Y akan di disable
        # karena pada histogram, sumbu Y akan menunjukkan kuantitas data

        # menu yang akan muncul di dropdown 'Estimator'
        focus_estimator='count',
        # menu yang akan tampil di dropdown 'Hue'
        focus_hue='vehicletype',
        # list yang akan digunakan looping untuk membuat dropdown 'Jenis Plot'
        drop_plot= list_plot,
        # list yang akan digunakan looping untuk membuat dropdown 'Sumbu X'
        drop_x= list_x,
        # list yang akan digunakan looping untuk membuat dropdown 'Sumbu Y'
        drop_y= list_y,
        # list yang akan digunakan looping untuk membuat dropdown 'Estimator'
        drop_estimator= list_est,
        # list yang akan digunakan looping untuk membuat dropdown 'Hue'
        drop_hue= list_hue)

# ada dua kondisi di mana kita akan melakukan request terhadap route ini
# pertama saat klik menu tab (Histogram & Box)
# kedua saat mengirim form (saat merubah salah satu dropdown) 
@app.route('/cat_fn/<nav>')
def cat_fn(nav):

    # saat klik menu navigasi
    if nav == 'True':
        cat_plot = 'histplot'
        cat_x = 'vehiclemodel'
        cat_y = 'ratedaily'
        estimator = 'count'
        hue = 'vehicletype'
    
    # saat memilih value dari form
    else:
        cat_plot = request.args.get('cat_plot')
        cat_x = request.args.get('cat_x')
        cat_y = request.args.get('cat_y')
        estimator = request.args.get('estimator')
        hue = request.args.get('hue')

    # Dari boxplot ke histogram akan None
    if estimator == None:
        estimator = 'count'
    
    # Saat estimator == 'count', dropdown menu sumbu Y menjadi disabled dan memberikan nilai None
    if cat_y == None:
        cat_y = 'ratedaily'

    # Dropdown menu
    list_plot = [('histplot', 'Histogram'), ('boxplot', 'Box')]
    list_x = [('vehiclemodel', 'Vehicle Model'), ('vehicletype', 'Vehicle Type'), ('locationstate', 'Location State'), ('vehicletype', 'Vehicle Type')]
    list_y = [('rating', 'Rating'), ('vehicleyear', 'Vehicle Year'), ('ratedaily', 'Rate Daily')]
    list_est = [('count', 'Count'), ('avg', 'Average'), ('max', 'Max'), ('min', 'Min')]
    list_hue = [('vehiclemodel', 'Vehicle Model'), ('vehicletype', 'Vehicle Type'), ('locationstate', 'Location State'), ('vehicletype', 'Vehicle Type')]

    plot = category_plot(cat_plot, cat_x, cat_y, estimator, hue)
    return render_template(
        # file yang akan menjadi response dari API
        'category.html',
        # plot yang akan ditampilkan
        plot=plot,
        # menu yang akan tampil di dropdown 'Jenis Plot'
        focus_plot=cat_plot,
        # menu yang akan muncul di dropdown 'sumbu X'
        focus_x=cat_x,
        focus_y=cat_y,

        # menu yang akan muncul di dropdown 'Estimator'
        focus_estimator=estimator,
        # menu yang akan tampil di dropdown 'Hue'
        focus_hue=hue,
        # list yang akan digunakan looping untuk membuat dropdown 'Jenis Plot'
        drop_plot= list_plot,
        # list yang akan digunakan looping untuk membuat dropdown 'Sumbu X'
        drop_x= list_x,
        # list yang akan digunakan looping untuk membuat dropdown 'Sumbu Y'
        drop_y= list_y,
        # list yang akan digunakan looping untuk membuat dropdown 'Estimator'
        drop_estimator= list_est,
        # list yang akan digunakan looping untuk membuat dropdown 'Hue'
        drop_hue= list_hue
    )

##################
## SCATTER PLOT ##
##################

# scatter plot function
def scatter_plot(cat_x, cat_y, hue):


    data = []

    for val in tips[hue].unique():
        scatt = go.Scatter(
            x = tips[tips[hue] == val][cat_x],
            y = tips[tips[hue] == val][cat_y],
            mode = 'markers',
            name = val
        )
        data.append(scatt)

    layout = go.Layout(
        title= 'Scatter',
        title_x= 0.5,
        xaxis=dict(title=cat_x),
        yaxis=dict(title=cat_y)
    )

    result = {"data": data, "layout": layout}

    graphJSON = json.dumps(result,cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

@app.route('/scatt_fn')
def scatt_fn():
    cat_x = request.args.get('cat_x')
    cat_y = request.args.get('cat_y')
    hue = request.args.get('hue')

    # WAJIB! default value ketika scatter pertama kali dipanggil
    if cat_x == None and cat_y == None and hue == None:
        cat_x = 'rating'
        cat_y = 'ratedaily'
        hue = 'vehiclemodel'

    # Dropdown menu
    list_x = [('rating', 'Rating'), ('vehicleyear', 'Vehicle Year'), ('ratedaily', 'Rate Daily')]
    list_y = [('rating', 'Rating'), ('vehicleyear', 'Vehicle Year'), ('ratedaily', 'Rate Daily')]
    list_hue = [('vehiclemodel', 'Vehicle Model'), ('vehicletype', 'Vehicle Type'), ('locationstate', 'Location State'), ('vehicletype', 'Vehicle Type')]

    plot = scatter_plot(cat_x, cat_y, hue)

    return render_template(
        'scatter.html',
        plot=plot,
        focus_x=cat_x,
        focus_y=cat_y,
        focus_hue=hue,
        drop_x= list_x,
        drop_y= list_y,
        drop_hue= list_hue
    )

##############
## PIE PLOT ##
##############

def pie_plot(hue = 'sex'):
    


    vcounts = tips[hue].value_counts()

    labels = []
    values = []

    for item in vcounts.iteritems():
        labels.append(item[0])
        values.append(item[1])
    
    data = [
        go.Pie(
            labels=labels,
            values=values
        )
    ]

    layout = go.Layout(title='Pie', title_x= 0.48)

    result = {'data': data, 'layout': layout}

    graphJSON = json.dumps(result,cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

@app.route('/pie_fn')
def pie_fn():
    hue = request.args.get('hue')

    if hue == None:
        hue = 'vehiclemodel'

    list_hue = [('vehiclemodel', 'Vehicle Model'), ('vehicletype', 'Vehicle Type'), ('locationstate', 'Location State'), ('vehicletype', 'Vehicle Type')]

    plot = pie_plot(hue)
    return render_template('pie.html', plot=plot, focus_hue=hue, drop_hue= list_hue)

###############
## UPDATE DB ##
###############
### Menampilkan data dari SQL
@app.route('/db_fn')
def db_fn():
    sqlengine = create_engine('mysql+pymysql://root:password@127.0.0.1/flaskapp', pool_recycle=3605)
    engine = sqlengine.raw_connection()
    cursor = engine.cursor()
    cursor.execute("SELECT * FROM tips")
    data = cursor.fetchall()
    return render_template('update.html', data=data)

@app.route('/update_fn', methods=['POST', 'GET'])
def update_fn():

    if request.method == 'POST':
        input = request.form
        
        locationstate = ''
        if input['locationstate'] == 'CA':
            location.state = 'CA'
        elif input['locationstate'] == 'FL':
            locationstate = 'FL'
        elif input['locationstate'] == 'NV':
            locationstate = 'NV'
        elif input['locationstate'] == 'NJ':
            locationstate = 'NJ'
        elif input['locationstate'] == 'TX':
            locationstate = 'TX'
        elif input['locationstate'] == 'CO':
            locationstate = 'CO'
        elif input['locationstate'] == 'AZ':
            locationstate = 'AZ'
        elif input['locationstate'] == 'OR':
            locationstate = 'OR'
        elif input['locationstate'] == 'GA':
            locationstate = 'UT'
        elif input['locationstate'] == 'IL':
            locationstate = 'lL'
        elif input['locationstate'] == 'VA':
            locationstate = 'VA'
        elif input['locationstate'] == 'NC':
            locationstate = 'NC'
        elif input['locationstate'] == 'HI':
            locationstate = 'HI'
        elif input['locationstate'] == 'OH':
            locationstate = 'OH'
        elif input['locationstate'] == 'WA':
            locationstate = 'WA'
        elif input['locationstate'] == 'TN':
            locationstate = 'TN'
        elif input['locationstate'] == 'MD':
            locationstate = 'MD'
        elif input['locationstate'] == 'MA':
            locationstate = 'MA'
        elif input['locationstate'] == 'MN':
            locationstate = 'MN'
        elif input['locationstate'] == 'PA':
            locationstate = 'PA'
        elif input['locationstate'] == 'OK':
            locationstate = 'OK'
        elif input['locationstate'] == 'MI':
            locationstate = 'MI'
        elif input['locationstate'] == 'SC':
            locationstate = 'SC'
        elif input['locationstate'] == 'IN':
            locationstate = 'IN'
        elif input['locationstate'] == 'KY':
            locationstate = 'KY'
        elif input['locationstate'] == 'KS':
            locationstate = 'KS'
        elif input['locationstate'] == 'WI':
            locationstate = 'WI'
        elif input['locationstate'] == 'NM':
            locationstate = 'MO'
        elif input['locationstate'] == 'AL':
            locationstate = 'AL'
        elif input['locationstate'] == 'RI':
            locationstate = 'RI'
        elif input['locationstate'] == 'LA':
            locationstate = 'LA'
        elif input['locationstate'] == 'IA':
            locationstate = 'IA'
        elif input['locationstate'] == 'ID':
            locationstate = 'ID'
        elif input['locationstate'] == 'NE':
            locationstate = 'NE'
        elif input['locationstate'] == 'ME':
            locationstate = 'ME'
        elif input['locationstate'] == 'CT':
            locationstate = 'CT'
        elif input['locationstate'] == 'AK':
            locationstate = 'AK'

        vehiclemake = ''
        if input['vehiclemake'] == 'Tesla':
            vehiclemake = 'Tesla'
        elif input['vehiclemake'] == 'Chevrolet':
            vehiclemake = 'Chevrolet'
        elif input['vehiclemake'] == 'BMW':
            vehiclemake = 'BMW'
        elif input['vehiclemake'] == 'Nissan':
            vehiclemake = 'Nissan'
        elif input['vehiclemake'] == 'Kia':
            vehiclemake = 'Kia'
        elif input['vehiclemake'] == 'smart':
            vehiclemake = 'smart'
        elif input['vehiclemake'] == 'Volkswagen':
            vehiclemake = 'Volkswagen'
        elif input['vehiclemake'] == 'FIAT':
            vehiclemake = 'FIAT'

        vehiclemodel = ''
        if input['vehiclemodel'] == 'Model 3':
            vehiclemodel = 'Model 3'
        elif input['vehiclemodel'] == 'Model S':
            vehiclemodel = 'Model S'
        elif input['vehiclemodel'] == 'Model X':
            vehiclemodel = 'Model X'    
        elif input['vehiclemodel'] == 'Model Y':
            vehiclemodel = 'Model Y'
        elif input['vehiclemodel'] == 'Bolt EV':
            vehiclemodel = 'Bolt EV'
        elif input['vehiclemodel'] == 'Leaf':
            vehiclemodel = 'Leaf'
        elif input['vehiclemodel'] == 'i3':
            vehiclemodel = 'i3'
        elif input['vehiclemodel'] == '500e':
            vehiclemodel = '500e'
        elif input['vehiclemodel'] == 'E-Golf':
            vehiclemodel = 'E-Golf'
        elif input['vehiclemodel'] == 'fortwo':
            vehiclemodel = 'fortwo'
        elif input['vehiclemodel'] == 'Soul EV':
            vehiclemodel = 'Soul EV'
        elif input['vehiclemodel'] == 'Niro':
            vehiclemodel = 'Niro'
        
        
        vehicletype = ''
        if input['vehicletype'] == 'car':
            vehicletype = 'car'
        else:
            vehicletype = 'car'
        ## Memasukkan data ke Tabel SQL
        new_df = pd.DataFrame({
            'ratedaily' : [int(input['ratedaily'])],
            'rating' : [float(input['rating'])],
            'vehiclemodel' : [vehiclemodel],
            'vehiclemake' : [vehiclemake],
            'locationstate' : [locationstate],
            'vehicletype' : [vehicletype],
            'vehicleyear' : [int(input['vehicleyear'])]
        })
        new_df.to_sql('tips', con=dbConnection, if_exists='append', index=False)
        return render_template('success.html',
            ratedaily=int(input['bill']),
            rating=float(input['rating']),
            vehiclemodel=vehiclemodel,
            vehiclemake=vehiclemake,
            locationstate=locationstate,
            vehicletype=vehicletype,
            vehicleyear=int(input['vehicleyear'])
            )


@app.route('/pred_lr')
## Menampilkan Dataset
def pred_lr():
    sqlengine = create_engine('mysql+pymysql://root:password@127.0.0.1/flaskapp', pool_recycle=3605)
    engine = sqlengine.raw_connection()
    cursor = engine.cursor()
    cursor.execute("SELECT * FROM tips")
    data = cursor.fetchall()
    return render_template('predict.html', data=data)

@app.route('/pred_result', methods=['POST', 'GET'])
def pred_result():

    if request.method == 'POST':
    ## Untuk Predict
        input = request.form
        
        locationstate = ''
        if input['locationstate'] == 'AK':
            locationstate = locationstate_AK =1
        else:
            locationstate = locationstate_AK= 0
        if input['locationstate'] == 'AK':
            locationstate = locationstate_AL =1
        else:
            locationstate = locationstate_AL = 0
        if input['locationstate'] == 'AZ':
            locationstate = locationstate_AZ =1
        else:
            locationstate = locationstate_AZ= 0
        if input['locationstate'] == 'CA':
            locationstate = locationstate_CA =1
        else:
            locationstate = locationstate_CA= 0
        if input['locationstate'] == 'CO':
            locationstate = locationstate_CO =1
        else:
            locationstate = locationstate_CO= 0        
        if input['locationstate'] == 'CT':
            locationstate = locationstate_CT =1
        else:
            locationstate = locationstate_CT= 0        
        if input['locationstate'] == 'FL':
            locationstate = locationstate_FL =1
        else:
            locationstate = locationstate_FL= 0        
        if input['locationstate'] == 'GA':
            locationstate = locationstate_GA =1
        else:
            locationstate = locationstate_GA= 0        
        if input['locationstate'] == 'HI':
            locationstate = locationstate_HI =1
        else:
            locationstate = locationstate_HI= 0        
        if input['locationstate'] == 'IH':
            locationstate = locationstate_IH =1
        else:
            locationstate = locationstate_IH= 0        
        if input['locationstate'] == 'ID':
            locationstate = locationstate_ID =1
        else:
            locationstate = locationstate_ID= 0        
        if input['locationstate'] == 'IL':
            locationstate = locationstate_IL =1
        else:
            locationstate = locationstate_IL= 0
        if input['locationstate'] == 'IA':
            locationstate = locationstate_IA =1
        else:
            locationstate = locationstate_IA= 0
        if input['locationstate'] == 'IN':
            locationstate = locationstate_IN =1
        else:
            locationstate = locationstate_IN= 0
        if input['locationstate'] == 'KS':
            locationstate = locationstate_KS =1
        else:
            locationstate = locationstate_KS= 0
        if input['locationstate'] == 'KY':
            locationstate = locationstate_KY =1
        else:
            locationstate = locationstate_KY= 0
        if input['locationstate'] == 'LA':
            locationstate = locationstate_LA =1
        else:
            locationstate = locationstate_LA= 0
        if input['locationstate'] == 'MA':
            locationstate = locationstate_MA =1
        else:
            locationstate = locationstate_MA= 0
        if input['locationstate'] == 'MD':
            locationstate = locationstate_MD =1
        else:
            locationstate = locationstate_MD= 0
        if input['locationstate'] == 'ME':
            locationstate = locationstate_ME =1
        else:
            locationstate = locationstate_ME= 0
        if input['locationstate'] == 'MI':
            locationstate = locationstate_MI =1
        else:
            locationstate = locationstate_MI= 0
        if input['locationstate'] == 'MN':
            locationstate = locationstate_MN =1
        else:
            locationstate = locationstate_MN= 0
        if input['locationstate'] == 'MO':
            locationstate = locationstate_MO =1
        else:
            locationstate = locationstate_MO= 0
        if input['locationstate'] == 'NC':
            locationstate = locationstate_NC =1
        else:
            locationstate = locationstate_NC= 0
        if input['locationstate'] == 'NE':
            locationstate = locationstate_NE =1
        else:
            locationstate = locationstate_NE= 0
        if input['locationstate'] == 'NJ':
            locationstate = locationstate_NJ =1
        else:
            locationstate = locationstate_NJ= 0
        if input['locationstate'] == 'NM':
            locationstate = locationstate_NM =1
        else:
            locationstate = locationstate_NM= 0
        if input['locationstate'] == 'NV':
            locationstate = locationstate_NV =1
        else:
            locationstate = locationstate_NV= 0
        if input['locationstate'] == 'OH':
            locationstate = locationstate_OH =1
        else:
            locationstate = locationstate_OH= 0
        if input['locationstate'] == 'ID':
            locationstate = locationstate_OK=1
        else:
            locationstate = locationstate_OK= 0
        if input['locationstate'] == 'OR':
            locationstate = locationstate_OR =1
        else:
            locationstate = locationstate_OR= 0
        if input['locationstate'] == 'PA':
            locationstate = locationstate_PA =1
        else:
            locationstate = locationstate_PA= 0
        if input['locationstate'] == 'RI':
            locationstate = locationstate_RI =1
        else:
            locationstate = locationstate_RI= 0
        if input['locationstate'] == 'SC':
            locationstate = locationstate_SC =1
        else:
            locationstate = locationstate_SC= 0
        if input['locationstate'] == 'TN':
            locationstate = locationstate_TN =1
        else:
            locationstate = locationstate_TN= 0
        if input['locationstate'] == 'TX':
            locationstate = locationstate_TX =1
        else:
            locationstate = locationstate_TX= 0
        if input['locationstate'] == 'UT':
            locationstate = locationstate_UT =1
        else:
            locationstate = locationstate_UT= 0
        if input['locationstate'] == 'UT':
            locationstate = locationstate_UT =1
        else:
            locationstate = locationstate_UT= 0
        if input['locationstate'] == 'VA':
            locationstate = locationstate_VA =1
        else:
            locationstate = locationstate_VA= 0
        if input['locationstate'] == 'WA':
            locationstate = locationstate_WA =1
        else:
            locationstate = locationstate_WA= 0
        if input['locationstate'] == 'WI':
            locationstate = locationstate_WI =1
        else:
            locationstate = locationstate_WI= 0
        if input['locationstate'] == 'UT':
            locationstate = locationstate_UT =1
        else:
            locationstate = locationstate_UT= 0
        
        vehiclemake=''
        if input['vehiclemake'] == 'BMW':
            vehiclemake = vehiclemake_BMW =1
        else:
            vehiclemake = vehiclemake_BMW = 0
        if input['vehiclemake'] == 'Tesla':
            vehiclemake = vehiclemake_Tesla =1
        else:
            vehiclemake = vehiclemake_Tesla = 0
        if input['vehiclemake'] == 'Nissan':
            vehiclemake = vehiclemake_Nissan =1
        else:
            vehiclemake = vehiclemake_Nissan = 0
        if input['vehiclemake'] == 'FIAT':
            vehiclemake = vehiclemake_FIAT =1
        else:
            vehiclemake = vehiclemake_FIAT = 0
        if input['vehiclemake'] == 'Volkswagen':
            vehiclemake = vehiclemake_Volkswagen =1
        else:
            vehiclemake = vehiclemake_Volkswagen = 0
        if input['vehiclemake'] == 'smart':
            vehiclemake = vehiclemake_smart =1
        else:
            vehiclemake = vehiclemake_smart = 0
        if input['vehiclemake'] == 'Chevrolet':
            vehiclemake = vehiclemake_Chevrolet =1
        else:
            vehiclemake = vehiclemake_Chevrolet = 0
        if input['vehiclemake'] == 'Kia':
            vehiclemake = vehiclemake_Kia =1
        else:
            vehiclemake = vehiclemake_Kia = 0


        vehiclemodel =''    
        if input['vehiclemodel'] == 'Model X':
            vehiclemodel = vehiclemodel_ModelX =1
        else:
            vehiclemodel = vehiclemodel_ModelX = 0
        if input['vehiclemodel'] == 'Model 3':
            vehiclemodel = vehiclemodel_Model3 =1
        else:
            vehiclemodel = vehiclemodel_Model3 = 0
        if input['vehiclemodel'] == 'Model S':
            vehiclemodel = vehiclemodel_ModelS =1
        else:
            vehiclemodel = vehiclemodel_ModelS = 0
        if input['vehiclemodel'] == 'Model Y':
            vehiclemodel = vehiclemodel_ModelY =1
        else:
            vehiclemodel = vehiclemodel_ModelY = 0
        if input['vehiclemodel'] == 'Leaf':
            vehiclemodel = vehiclemodel_Leaf =1
        else:
            vehiclemodel = vehiclemodel_Leaf = 0
        if input['vehiclemodel'] == 'i3':
            vehiclemodel = vehiclemodel_i3 =1
        else:
            vehiclemodel = vehiclemodel_i3 = 0
        if input['vehiclemodel'] == 'BoltEV':
            vehiclemodel = vehiclemodel_BoltEV =1
        else:
            vehiclemodel = vehiclemodel_BoltEV = 0
        if input['vehiclemodel'] == '500e':
            vehiclemodel = vehiclemodel_500e =1
        else:
            vehiclemodel = vehiclemodel_500e = 0
        if input['vehiclemodel'] == 'E-Golf':
            vehiclemodel = vehiclemodel_EGolf =1
        else:
            vehiclemodel = vehiclemodel_EGolf = 0
        if input['vehiclemodel'] == 'Niro':
            vehiclemodel = vehiclemodel_Niro =1
        else:
            vehiclemodel = vehiclemodel_Niro = 0
        if input['vehiclemodel'] == 'fortwo':
            vehiclemodel = vehiclemodel_fortwo =1
        else:
            vehiclemodel = vehiclemodel_fortwo = 0
        if input['vehiclemodel'] == 'Soul EV':
            vehiclemodel = vehiclemodel_SoulEV =1
        else:
            vehiclemodel = vehiclemodel_SoulEV = 0
        
        vehicletype=''
        if input['vehicletype'] == 'car':
            vehicletype = vehicletype_car =1
        else:
            vehicletype = vehicletype_car = 0
        
        if input['vehicletype'] == 'suv':
            vehicletype = vehicletype_suv =1
        else:
            vehicletype = vehicletype_suv = 0
        
        
        vehicleyear=int(input['vehicleyear'])
        rating = int(input['rating'])

        pred = model.predict([[rating,vehicleyear,locationstate_AK,locationstate_AL,locationstate_AZ,locationstate_CA,locationstate_CO,locationstate_CT,locationstate_FL,locationstate_GA,locationstate_HI,locationstate_IA,locationstate_ID,locationstate_IL,locationstate_IN,locationstate_KS,locationstate_KY,locationstate_LA,locationstate_MA,locationstate_MD,locationstate_ME,locationstate_MI,locationstate_MN,locationstate_MO,locationstate_NC,locationstate_NE,locationstate_NJ,locationstate_NM,locationstate_NV,locationstate_OH,locationstate_OK,locationstate_OR,locationstate_PA,locationstate_RI,locationstate_SC,locationstate_TN,locationstate_TX,locationstate_UT,locationstate_VA,locationstate_WA,locationstate_WI,vehiclemake_BMW,vehiclemake_Chevrolet,vehiclemake_FIAT,vehiclemake_Kia,vehiclemake_Nissan,vehiclemake_Tesla,vehiclemake_Volkswagen,vehiclemake_smart,vehiclemodel_500e,vehiclemodel_BoltEV,vehiclemodel_EGolf,vehiclemodel_Leaf,vehiclemodel_Model3,vehiclemodel_ModelS,vehiclemodel_ModelX,vehiclemodel_ModelY,vehiclemodel_Niro,vehiclemodel_SoulEV,vehiclemodel_fortwo,vehiclemodel_i3,vehicletype_car,vehicletype_suv]])[0].round(2)

        ## Untuk Isi Data
        vehicleyear_dt = ''
        if input['vehicletype'] == 'car':
            vehicletype_dt = 'car'
        else:
            vehicletype_dt = 'suv'
        locationstate_dt = ''
        if input['locationstate'] == 'CA':
            location.state_dt = 'CA'
        elif input['locationstate'] == 'FL':
            locationstate_dt = 'FL'
        elif input['locationstate'] == 'NV':
            locationstate_dt = 'NV'
        elif input['locationstate'] == 'NJ':
            locationstate_dt = 'NJ'
        elif input['locationstate'] == 'TX':
            locationstate_dt = 'TX'
        elif input['locationstate'] == 'CO':
            locationstate_dt = 'CO'
        elif input['locationstate'] == 'AZ':
            locationstate_dt = 'AZ'
        elif input['locationstate'] == 'OR':
            locationstate_dt = 'OR'
        elif input['locationstate'] == 'GA':
            locationstate_dt = 'UT'
        elif input['locationstate'] == 'IL':
            locationstate_dt = 'lL'
        elif input['locationstate'] == 'VA':
            locationstate_dt = 'VA'
        elif input['locationstate'] == 'NC':
            locationstate_dt = 'NC'
        elif input['locationstate'] == 'HI':
            locationstate_dt = 'HI'
        elif input['locationstate'] == 'OH':
            locationstate_dt = 'OH'
        elif input['locationstate'] == 'WA':
            locationstate_dt = 'WA'
        elif input['locationstate'] == 'TN':
            locationstate_dt = 'TN'
        elif input['locationstate'] == 'MD':
            locationstate_dt = 'MD'
        elif input['locationstate'] == 'MA':
            locationstate_dt = 'MA'
        elif input['locationstate'] == 'MN':
            locationstate_dt = 'MN'
        elif input['locationstate'] == 'PA':
            locationstate_dt = 'PA'
        elif input['locationstate'] == 'OK':
            locationstate_dt = 'OK'
        elif input['locationstate'] == 'MI':
            locationstate_dt = 'MI'
        elif input['locationstate'] == 'SC':
            locationstate_dt = 'SC'
        elif input['locationstate'] == 'IN':
            locationstate_dt = 'IN'
        elif input['locationstate'] == 'KY':
            locationstate_dt = 'KY'
        elif input['locationstate'] == 'KS':
            locationstate_dt = 'KS'
        elif input['locationstate'] == 'WI':
            locationstate_dt = 'WI'
        elif input['locationstate'] == 'NM':
            locationstate_dt = 'MO'
        elif input['locationstate'] == 'AL':
            locationstate_dt = 'AL'
        elif input['locationstate'] == 'RI':
            locationstate_dt = 'RI'
        elif input['locationstate'] == 'LA':
            locationstate_dt = 'LA'
        elif input['locationstate'] == 'IA':
            locationstate_dt = 'IA'
        elif input['locationstate'] == 'ID':
            locationstate_dt = 'ID'
        elif input['locationstate'] == 'NE':
            locationstate_dt = 'NE'
        elif input['locationstate'] == 'ME':
            locationstate_dt = 'ME'
        elif input['locationstate'] == 'CT':
            locationstate_dt = 'CT'
        elif input['locationstate'] == 'AK':
            locationstate_dt = 'AK'

        vehiclemake_dt = ''
        if input['vehiclemake'] == 'Tesla':
            vehiclemake_dt = 'Tesla'
        elif input['vehiclemake'] == 'Chevrolet':
            vehiclemake_dt = 'Chevrolet'
        elif input['vehiclemake'] == 'BMW':
            vehiclemake_dt = 'BMW'
        elif input['vehiclemake'] == 'Nissan':
            vehiclemake_dt = 'Nissan'
        elif input['vehiclemake'] == 'Kia':
            vehiclemake_dt = 'Kia'
        elif input['vehiclemake'] == 'smart':
            vehiclemake_dt = 'smart'
        elif input['vehiclemake'] == 'Volkswagen':
            vehiclemake_dt = 'Volkswagen'
        elif input['vehiclemake'] == 'FIAT':
            vehiclemake_dt = 'FIAT'

        vehiclemodel_dt = ''
        if input['vehiclemodel'] == 'Model 3':
            vehiclemodel_dt = 'Model 3'
        elif input['vehiclemodel'] == 'Model S':
            vehiclemodel_dt = 'Model S'
        elif input['vehiclemodel'] == 'Model X':
            vehiclemodel_dt = 'Model X'    
        elif input['vehiclemodel'] == 'Model Y':
            vehiclemodel_dt = 'Model Y'
        elif input['vehiclemodel'] == 'Bolt EV':
            vehiclemodel_dt = 'Bolt EV'
        elif input['vehiclemodel'] == 'Leaf':
            vehiclemodel_dt = 'Leaf'
        elif input['vehiclemodel'] == 'i3':
            vehiclemodel_dt = 'i3'
        elif input['vehiclemodel'] == '500e':
            vehiclemodel_dt = '500e'
        elif input['vehiclemodel'] == 'E-Golf':
            vehiclemodel_dt = 'E-Golf'
        elif input['vehiclemodel'] == 'fortwo':
            vehiclemodel_dt = 'fortwo'
        elif input['vehiclemodel'] == 'Soul EV':
            vehiclemodel_dt = 'Soul EV'
        elif input['vehiclemodel'] == 'Niro':
            vehiclemodel_dt = 'Niro'
        

        return render_template('result.html',
            rating=int(input['rating']),
            vehiclemodel=vehiclemodel_dt,
            vehicletype=vehicletype_dt,
            vehiclemake=vehiclemake_dt,
            locationstate=locationstate_dt,
            vehicleyear=int(input['vehicleyear']),
            tip_pred = pred
            )

if __name__ == '__main__':
    ## Me-Load data dari Database
    sqlengine = create_engine('mysql+pymysql://root:password@127.0.0.1/flaskapp', pool_recycle=3605)
    dbConnection = sqlengine.connect()
    engine = sqlengine.raw_connection()
    cursor = engine.cursor()
    # tips = pd.read_sql("select * from tips", dbConnection)
    tips = pd.read_csv('cek.csv')
    ## Load Model
    model = joblib.load('model')
    app.run(debug=True)