import boto3
#########################################################################################
# aws-list-services.py                                                                  #
#                                                                                       #
#  Function......List VpC, Instances,LaodBalancer, Lambda Security Groups , ECS, EKS    #
#  Requires......https://aws.amazon.com/sdk-for-python/                                 #
#  Released......March 11, 2021                                                         #
#  Scripter......                                                                       #
#  Invoke........python3 aws-list-services.py                                           #
#                                                                                       #
#########################################################################################

class myList:
    def GetRegions(self):
        RegionList = []
        region=boto3.client('ec2')
        Response=region.describe_regions()
        for RegionCount in range(len(Response['Regions'])):
            RegionList.append(Response['Regions'][RegionCount]['RegionName'])
        print("Number of Regions {}".format(len(RegionList)))
        print("Regions::")
        print (RegionList)
        print("**********************************")
        return RegionList

    def ListEc2Instance(self):
        FetchRegionList=[]
        FetchRegionList=self.GetRegions()
        for Region in range(len(FetchRegionList)):
            print("**********************************")
            print ("Region : --> {}".format(FetchRegionList[Region]))
            #Find all VPC in a Region
            Ec2 = boto3.client('ec2', region_name=FetchRegionList[Region])
            vpcs = Ec2.describe_vpcs()
            for vpc in vpcs['Vpcs']:
                print("VPC --> VPCId : {}. CidrBlock : {}. DefaultVPC? : {}. ".format(vpc['VpcId'],vpc['CidrBlock'],vpc['IsDefault']))

            #Fetch security groups used in Region
            GetSecurityGroup = Ec2.describe_security_groups()
            if len(GetSecurityGroup['SecurityGroups']) !=0:
                for SecurityGroupCount in range(len(GetSecurityGroup['SecurityGroups'])):
                    GroupId = GetSecurityGroup['SecurityGroups'][SecurityGroupCount]['GroupId']
                    VpcId = GetSecurityGroup['SecurityGroups'][SecurityGroupCount]['VpcId']
                    GroupName = GetSecurityGroup['SecurityGroups'][SecurityGroupCount]['GroupName']
                    print ("Security --> Groupid : {}. VpcId : {}. GroupName : {}.".format(GroupId,VpcId,GroupName))
            else:
                print ("No security group available for this region.")

            #Find all Ec2 instance in Region.
            GetInstance = Ec2.describe_instances()
            if len(GetInstance['Reservations']) != 0:
                for InstanceCount in range(len(GetInstance['Reservations'])):
                    InstID=GetInstance['Reservations'][InstanceCount]['Instances'][0]['InstanceId']
                    InstType=GetInstance['Reservations'][InstanceCount]['Instances'][0]['InstanceType']
                    InstState=GetInstance['Reservations'][InstanceCount]['Instances'][0]['State']['Name']
                    print ("EC2 Instance --> id : {}. InstanceType: {}. Status : {}.".format(InstID,InstType,InstState))
            else:
                print ("No EC2 Instance(s) running in Region.")

            #Find all volumes used in Region:
            GetVolume = Ec2.describe_volumes()
            if len(GetVolume['Volumes']) !=0:
                for VolumeCount in range(len(GetVolume['Volumes'])):
                    GetVolumeID=GetVolume['Volumes'][VolumeCount]['VolumeId']
                    GetDiskState=GetVolume['Volumes'][VolumeCount]['State']
                    GetVolumeType=GetVolume['Volumes'][VolumeCount]['VolumeType']
                    GetVolumeSize = GetVolume['Volumes'][VolumeCount]['Size']
                    print ("Disk --> Volumeid : {}. VolumeState: {}. VolumeType: {}. VolumeSize {}".format(GetVolumeID,GetDiskState, \
                        GetVolumeType,GetVolumeSize))
            else:
                print ("No Volumes found in Region.")

            #Find all ELBv2 loadbalancer running in Region.
            ELBLoad = boto3.client('elbv2', region_name=FetchRegionList[Region])
            ELBv2 = ELBLoad.describe_load_balancers()
            if len(ELBv2['LoadBalancers']) != 0:
                for ElbCount in range(len(ELBv2['LoadBalancers'])):
                    LBname = ELBv2['LoadBalancers'][ElbCount]['LoadBalancerName']
                    LBState = ELBv2['LoadBalancers'][ElbCount]['State']['Code']
                    LBType = ELBv2['LoadBalancers'][ElbCount]['Type']
                    print ("Loadbalancer --> LBName : {}. LBState : {}. LBType : {}".format(LBname,LBState,LBType))
            else:
                print ("No LoadBalancer found in Region.")

            #Find all Lambda functions running in Region.
            Lmbda = boto3.client('lambda',region_name=FetchRegionList[Region])
            LambdaLst = Lmbda.list_functions()
            if len(LambdaLst['Functions']) != 0:
                for FncCount in range(len(LambdaLst['Functions'])):
                    FncName = LambdaLst['Functions'][FncCount]['FunctionName']
                    FncMem = LambdaLst['Functions'][FncCount]['MemorySize']
                    FncCodeSize = LambdaLst['Functions'][FncCount]['CodeSize']
                    FncRuntime = LambdaLst['Functions'][FncCount]['Runtime']
                    print ("Lambda Function --> Name : {}. Memory : {}. CodeSize : {}. Runtime : {}.".format(FncName, \
                        FncMem,FncCodeSize,FncRuntime))
            else:
                print ("No Lambda function available in Region.")


            # #Fetch security groups used in Region
            # GetSecurityGroup = Ec2.describe_security_groups()
            # if len(GetSecurityGroup['SecurityGroups']) !=0:
            #     for SecurityGroupCount in range(len(GetSecurityGroup['SecurityGroups'])):
            #         GroupId = GetSecurityGroup['SecurityGroups'][SecurityGroupCount]['GroupId']
            #         VpcId = GetSecurityGroup['SecurityGroups'][SecurityGroupCount]['VpcId']
            #         GroupName = GetSecurityGroup['SecurityGroups'][SecurityGroupCount]['GroupName']
            #         print ("Security --> Groupid : {}. VpcId : {}. GroupName : {}.".format(GroupId,VpcId,GroupName))
            # else:
            #     print ("No security group available for this region.")

            #Fetch ecs
            ecs = boto3.client('ecs',region_name=FetchRegionList[Region])
            response = ecs.list_clusters(maxResults=100)
            if len(response['clusterArns'])!=0:
                desc = ecs.describe_clusters(
                    clusters=response['clusterArns'])
                [print("ECS --> ClusterName : {}. clusterArn : {}. clusterStatus : {}. registeredContainerInstancesCount : {}. runningTasksCount : {}. pendingTasksCount : {}. activeServicesCount : {}".
                       format(each['ClusterName'],each['clusterArn'],each['clusterStatus'],each['registeredContainerInstancesCount'],each['runningTasksCount'],each['pendingTasksCount'],each['activeServicesCount'])) for each in desc['clusters']]
            else:
                print("No ECS Cluster(s) running in Region.")

            # Fetch eks
            eks = boto3.client('eks', region_name=FetchRegionList[Region])
            response = eks.list_clusters(maxResults=100)
            if len(response['clusters']) != 0:
                for each in response['clusters']:
                    eks_cluster_det = eks.describe_cluster(
                        name=each
                    )
                    print("EKS --> ClusterName : {}. ClusterStatus : {}. ClusterArn : {}.".format(eks_cluster_det['cluster']['name'],eks_cluster_det['cluster']['status'],eks_cluster_det['cluster']['arn']))
            else:
                print("No EKS Cluster(s) running in Region.")

            # # fetch all buckets
            # s3 = boto3.client('s3', region_name=FetchRegionList[Region])
            # s3_resp = s3.list_buckets()
            # if len(s3_resp['Buckets'])!=0:
            #     for each in s3_resp['Buckets']:
            #         print("S3 --> BucketName : {}. CreationDate: {}".format(each['Name'],each['CreationDate']))
            # else:
            #     print("No S3 bucket present in this Region")
                
        print("**********************************")
        # Fetch domain
        client = boto3.client('route53domains')
        response = client.list_domains()
        if len(response['Domains'])!=0:
            for each in response['Domains']:
                print("Route 53 --> DomainName : {}. AutoRenewEnabled? : {}. ExpiryDate : {}.".format(each['DomainName'], each['AutoRenew'], each['Expiry']))
        else:
            print("No DNS Record found")
        print("**********************************")


if __name__ == '__main__':
    RunQuery = myList()
    RunQuery.ListEc2Instance()
