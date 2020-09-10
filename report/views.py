from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import os
from PIL import Image  #may be login_required
import pandas as pd
import matplotlib.pyplot as plt
import mpld3
import json  ###graph
from datetime import datetime
import io
import urllib,base64
from django.http import HttpResponse
# from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
# from matplotlib.figure import Figure
from plotly.offline import plot
from plotly.graph_objs import Scatter


# Create your views here.
def home(request):
    name="Prachi"
    return render(request,'report/home.html',{'name':name})

def analyse(request):
    fileObj=request.FILES['filePath']
    fs=FileSystemStorage()
    filePathName=fs.save(fileObj.name,fileObj)
    file_name=os.path.join('./media',filePathName)
    # sheet=sheet
    sheet=request.POST['sheet']
    start_date=request.POST['trip-start']
    end_date=request.POST['trip-end']

    start_date=datetime.strptime(start_date, '%Y-%m-%d')
    end_date=datetime.strptime(end_date, '%Y-%m-%d')

    print(start_date)
    my_workbook=pd.read_excel(file_name,sheet_name=sheet)
    filePathName=fs.url(filePathName)
    my_workbook.fillna(0,inplace=True)

    file_column=my_workbook.columns
    row=my_workbook.shape[0]
    col=my_workbook.shape[1]
    i=2
    start_index=row
    end_index=col
    for i in range(col):
        if(file_column[i] == start_date):
            start_index=i
            break;
    for i in range(col):
        if(file_column[i] == end_date):
            end_index=i
            break;

    date=[]
    date.append(my_workbook.columns[start_index:end_index+1])

    total_present_of_students=(my_workbook.iloc[:,start_index:end_index+1].sum()).astype(int)
    total_present_in_percent=((my_workbook.iloc[:,start_index:end_index+1].sum())/row*100).astype(int)
    first_output=pd.DataFrame({"total_present_of_students":total_present_of_students,
                                "total_present_of_students_in_percent":total_present_in_percent})

    print(first_output.columns)



    #graphs


# def index(request):
    x_data=date
    y_data = first_output.total_present_of_students
    plot_div1 = plot([Scatter(y=y_data,
                        mode='lines', name='test',
                        opacity=0.8, marker_color='green')],
               output_type='div')

    y_data = first_output.total_present_of_students_in_percent
    plot_div2 = plot([Scatter(y=y_data,
                        mode='lines', name='test',
                        opacity=0.8, marker_color='green')],
               output_type='div')
    # return render(request, "graphics/base.html", context={'fig': plot_div})

    #
    # fig, ax = plt.subplots()
    # ax.plot(first_output.total_present_of_students_in_percent);
    # result=fig.autofmt_xdate()
    # single_chart=dict()
    # single_chart['id']="fig_01"
    # single_chart['json']=json.dumps(mpld3.fig_to_dict(fig))
    # result={'single_chart':single_chart}
    # plt.close()
    # buf=io.BytesIO()
    # fig.savefig(buf,format='png')
    # buf.seek(0)
    # string=base64.b64encode(buf.read())
    # uri=urllib.parse.quote(string)
    # plt.show()

    # plot_div.set_xlabel('Date Wise data')
    # plot_div.set_ylabel('Total number present of students in percent')
    # plot_div.set_title("Report 1")
    #
    # canvas = FigureCanvas(fig)
    # response = HttpResponse(content_type='image/png')
    # print(result)
    # print(type(result))

    total=[]
    i=0
    for i in range((row)):
        total.append(int(my_workbook.iloc[i,start_index:end_index+1].sum()))


    my_workbook["total"]=total
    maximum=max(total)
    total_percentage_of_present_of_particular_student=[]
    for i in range(len(total)):
        total_percentage_of_present_of_particular_student.append(total[i]/maximum*100)

    df=pd.DataFrame({"rollnumber":my_workbook.rollnumber,
                "percentage_wise":total_percentage_of_present_of_particular_student,
                "total_number_of_presents":total})

    print(df)

    less_than_25=df[df.percentage_wise<26]
    less_25=len(less_than_25)
    print(less_than_25)

    less_than_50=df[df.percentage_wise<50]
    less_50=len(less_than_50)

    less_than_75=df[df.percentage_wise<75]
    less_75=len(less_than_75)

    greater_than_75=df[df.percentage_wise>75]
    greater_75=len(greater_than_75)


    if request.method == "POST":
        return render(request,'report/analyse.html',{'p':filePathName,'file':file_name,'sheet':sheet,'start':start_date.date(),'end':end_date.date(),'teacher':first_output.to_html(),'student':df.to_html(),'less_than_25':less_than_25.to_html(),'less_than_50':less_than_50.to_html(),'less_than_75':less_than_75.to_html(),'greater_than_75':greater_than_75.to_html(),'less_25':less_25,'less_50':less_50,'less_75':less_75,'greater_75':greater_75,'graph1':plot_div1,'graph2':plot_div2})
