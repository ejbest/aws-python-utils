import boto3
import os
#########################################################################################
# key_rotator.py                                                                        #
#                                                                                       #
#  Function......Will get new keys for all keys in ~/.aws/credentials                   #
#  Requires......https://aws.amazon.com/sdk-for-python/                                 #
#  Released......March 11, 2021                                                         #
#  Scripter......                                                                       #
#  Invoke........python3 aws-list-services.py                                           #
#                                                                                       #
#########################################################################################
os.system('cp ~/.aws/credentials ~/.aws/credentials.sav')
file_path = "/Users/ej/.aws/credentials"
re_write_path = '/Users/ej/.aws/credentials'


def rotate_key(old_acc,old_sec):
    iam = boto3.client('iam',aws_access_key_id=old_acc, aws_secret_access_key=old_sec)
    # create a new access key
    response = iam.create_access_key()
    if response['AccessKey']['Status'] == 'Active':
        new_Acc = response['AccessKey']['AccessKeyId']
        new_Sec = response['AccessKey']['SecretAccessKey']
        del_response = iam.delete_access_key(
            AccessKeyId=old_acc
        )
        if del_response['ResponseMetadata']['HTTPStatusCode']==200:
            print("Successfully rotated keys")
            return new_Acc,new_Sec

# use this to test
def dummy(acc,sec):
    return acc,sec

dic = []
email = []
index =0
new_cred = ""
with open(file_path) as fp:
    data= fp.readlines()
    #print(data)
    for each in data:
        if '#aws_access_key_id' in each:
            acc = each.split("=")[1].strip()
            dic.append({"acc":acc,"sec":""})
            new_cred+="#aws_access_key_id = {}\n"
        elif '#aws_secret_access_key' in each:
            sec = each.split('=')[1].strip()
            dic[index]["sec"]=sec
            new_cred += "#aws_secret_access_key = {}\n"
            access_flag=0
            index += 1

        elif 'aws_access_key_id' in each:
            acc = each.split("=")[1].strip()
            dic.append({"acc":acc,"sec":""})
            new_cred+="aws_access_key_id = {}\n"

        elif 'aws_secret_access_key' in each:
            sec = each.split('=')[1].strip()
            dic[index]["sec"]=sec
            new_cred += "aws_secret_access_key = {}\n"
            access_flag=0
            index += 1
        else:
            new_cred+=each

format_list = []
for each in dic:
    format_list.extend(rotate_key(each['acc'],each['sec']))

new_cred = new_cred.format(*format_list)
#print(new_cred)
with open(re_write_path,"w") as fp:
    fp.write(new_cred)
