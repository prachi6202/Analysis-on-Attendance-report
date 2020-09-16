from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from django.http import HttpResponse
import numpy as np
import requests
from plotly.offline import plot
from plotly.graph_objs import Scatter
# import plotly.graph_objs
from xlrd import XLRDError
import plotly.express as px
from django.http import HttpResponse, HttpResponseRedirect
# Create your views here.

def home(request):
    return render(request,'report/home.html')

def about(request):
    return render(request,'report/about.html')

def analyse(request):
    fileObj=request.FILES['filePath']
    fs=FileSystemStorage()
    filePathName=fs.save(fileObj.name,fileObj)
    file_name=os.path.join('./media',filePathName)

    sheet=request.POST['sheet']
    start_date=request.POST['trip-start']
    end_date=request.POST['trip-end']

    num=request.POST['number']
    num=int(num)

    start_date=datetime.strptime(start_date, '%Y-%m-%d')
    end_date=datetime.strptime(end_date, '%Y-%m-%d')

    if(0 <= num <=100):

        try:
            my_workbook=pd.read_excel(file_name,sheet_name=sheet,index_col=False)
            filePathName=fs.url(filePathName)
            my_workbook.fillna(0,inplace=True)

            file_column=my_workbook.columns
            row=my_workbook.shape[0]
            col=my_workbook.shape[1]
            i=3
            start_index=i
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
            date=np.array(date)
            date=date.flatten()


            total_present_of_students=(my_workbook.iloc[:,start_index:end_index+1].sum()).astype(int)
            total_present_in_percent=((my_workbook.iloc[:,start_index:end_index+1].sum())/row*100).astype(int)
            first_output=pd.DataFrame({"Students":total_present_of_students,
                                        "Percentage":total_present_in_percent})


            values=[]
            values=first_output[first_output.Percentage != 0]
            percentage_of_class=(first_output['Percentage'].sum())/row

            values=pd.DataFrame(values)

            graph=pd.DataFrame({"Date":date,
                                "Students":total_present_of_students,
                                "Percentage":total_present_in_percent,
                                })

            y = graph.Students
            x = graph.Date
            plot_div1 = plot([Scatter(x=x, y=y,
                        mode='lines', name='test',
                        opacity=0.8, marker_color='blue')],
                        output_type='div')

            y = graph.Percentage
            x = graph.Date
            plot_div2 = plot([Scatter(x=x, y=y,
                        mode='lines', name='test',
                        opacity=0.8, marker_color='blue')],
                        output_type='div')

            fig1 = px.bar(x=graph.Date, y=graph.Percentage, labels={'x':'Date', 'y':'Student %'})
            fig2 = px.bar(x=graph.Date, y=graph.Students, labels={'x':'Date', 'y':'Student'})


            total=[]
            i=0
            for i in range((row)):
                total.append(int(my_workbook.iloc[i,start_index:end_index+1].sum()))


            my_workbook["total"]=total
            maximum=max(total)
            total_percentage_of_present_of_particular_student=[]
            for i in range(len(total)):
                total_percentage_of_present_of_particular_student.append(total[i]/maximum*100)


            roll=np.array(my_workbook.iloc[:,1:2])
            roll=roll.flatten()
            name=np.array(my_workbook.iloc[:,2:3])
            name=name.flatten()

            df=pd.DataFrame({"Rollnumber":roll.astype(str),
                            "Name  ":name,
                            "Total":total,
                            "Percentage":total_percentage_of_present_of_particular_student,})

            df_print=df.to_string(index=False)
            less_than_25=df[df.Percentage < num+1]
            less_25=len(less_than_25)
            print(less_than_25)

            if request.method == "POST":
                return render(request,'report/analyse.html',{'p':filePathName,'file':file_name,'sheet':sheet,'start':start_date.date(),'end':end_date.date(),'teacher':first_output.to_html(),'student':df.to_html(),'less_than_25':less_than_25.to_html(),
                                'less_25':less_25,'num':num,'values':values.to_html(),'plot_div1':plot_div1,'plot_div2':plot_div2,'fig1':fig1.to_html,'fig2':fig2.to_html})

        except ZeroDivisionError:
            return HttpResponse("No record found. Check your file. Go Back")

        except XLRDError:
            return HttpResponse("Wrong File or Wrong Sheet Name. Go Back")

        except ValueError:
            return HttpResponse("You have enter the wrong value. Go Back")

        except RuntimeError:
            return render(request,'report/home.html')

        except MultiValueDictKeyError:
            return HttpResponse("Enter File. You have entered wrong input.Go Back")

    else:
        return HttpResponse("Did you mean this ? Choose the correct input.Go Back")
