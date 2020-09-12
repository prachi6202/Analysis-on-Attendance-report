from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from django.http import HttpResponse
import numpy as np
import requests
from xlrd import XLRDError
# Create your views here.

def home(request):
    return render(request,'report/home.html')

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
        first_output=pd.DataFrame({"Number_of_Students_Presented":total_present_of_students,
                                    "Percentage":total_present_in_percent})


        values=[]
        values=first_output[first_output.Percentage != 0]
        percentage_of_class=(first_output['Percentage'].sum())/row

        values=pd.DataFrame(values)

        y=first_output.Number_of_Students_Presented
        y=np.array(y)
        y=y.flatten()
        fig, ax = plt.subplots()
        ax.bar(date,y);
        result=fig.autofmt_xdate()
        # plt.xlabel("Date")
        plt.ylabel("Total Students Presented")
        plt.savefig('media/abhi.png', dpi=300)

        y=first_output.Percentage
        y=np.array(y)
        y=y.flatten()
        fig, ax = plt.subplots()
        ax.bar(date,y);
        result=fig.autofmt_xdate()
        plt.ylabel("Total Students Presented (%age)")
        plt.savefig('media/naman.png', dpi=300)


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

        df=pd.DataFrame({"Rollnumber":roll.astype(int),
                        "Name  ":name,
                        "Total":total,
                        "Percentage":total_percentage_of_present_of_particular_student,})

        df_print=df.to_string(index=False)
        less_than_25=df[df.Percentage < num+1]
        less_25=len(less_than_25)
        print(less_than_25)

        if request.method == "POST":
            return render(request,'report/analyse.html',{'p':filePathName,'file':file_name,'sheet':sheet,'start':start_date.date(),'end':end_date.date(),'teacher':first_output.to_html(),'student':df.to_html(),'less_than_25':less_than_25.to_html(),'less_25':less_25,'num':num,'values':values.to_html()})

    except ZeroDivisionError:
        return HttpResponse("No data in file.Check your file.")

    except XLRDError:
        return HttpResponse("Wrong File or Wrong Sheet Name")

    except ValueError:
        return HttpResponse("You have enter the wrong value")
