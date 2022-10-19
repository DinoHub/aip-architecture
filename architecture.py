from turtle import pensize
from diagrams import Cluster, Diagram, Edge
from diagrams.k8s.network import Ing
from diagrams.k8s.network import Ep, SVC
from diagrams.k8s.infra import Master, Node
from diagrams.k8s.compute import Pod
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB
from diagrams.aws.storage import S3
from diagrams.k8s.group import NS
from diagrams.onprem.client import Client, User, Users
from diagrams.onprem.compute import Server
from diagrams.onprem.vcs import Gitlab
from diagrams.onprem.network import Nginx
from diagrams.k8s.clusterconfig import HPA
from diagrams.onprem.monitoring import Prometheus, Grafana
from diagrams.oci.storage import ObjectStorage
from diagrams.custom import Custom
from diagrams.onprem.ci import Gitlabci
from diagrams.onprem.workflow import Nifi
            
from diagrams.onprem.queue import Kafka

graph_attr = {
    "fontsize": "45",
    "nojustify": 'true',
   # "bgcolor": "transparent"
}


with Diagram("AI Platform (Dev)", show=True, graph_attr=graph_attr, direction="LR"):
    
    

    with Cluster("Client Zone"):
        clients = Client("Clients")
        labelstudio=Custom("Label Studio","./labelstudio.png")


    with Cluster("Server Zone"):

        with Cluster("VM"):
            gitlabserver=Gitlab('SCM')
            harborserver=Custom("Image Repo","./harbor-icon-color.png")
            gitlabci=Gitlabci("GitLab CI")
            objectstore=Custom("Object Store","./minio.png")
            libraries=Custom("Libraries","./jfrogartifactory.png")

        with Cluster("Staging"):
            nifi=Nifi("Apache NiFi")
            kafka=Kafka("Kafka Messaging")
            customApp=Server("Custom Apps")

        with Cluster("Kubernetes"):

            with Cluster("Cluster"):
                ingress = Nginx("ingress")        
                with Cluster("Pods"):
                    clearmlserver=Pod('ClearML-Server')
                    clearmlagent=Pod('ClearML-Agent')
                    clearmlserving=Pod('ClearML-Serving')
                    mljob=Pod('MLJob')                    
                    podscaler=HPA("HPA")
                    tritonserver=Pod('Triton')
                    prometheus=Prometheus('Metrics')
                    grafana=Grafana('Monitoring')
                    customApi=Pod('Custom APIs')
                        
                with Cluster("Services"):
                    clearmlapi= SVC("ClearML API Svc")
                    clearmlfile=SVC("ClearML File Svc")
                    clearmlweb=SVC("ClearML Web Svc")
                    tritonsvc=SVC("Triton Svc")

                
                ingress \
                    >> Edge() \
                    >> [clearmlapi,clearmlfile,clearmlweb, tritonsvc]
                
                #Prometheus interactions
                prometheus >> Edge() >> grafana
                
                #services visual positioning
                servicesordering=clearmlapi - Edge(penwidth='0') - clearmlfile - Edge(penwidth='0') - clearmlweb -Edge(penwidth='0') - tritonsvc

                # ClearML internal interactions
                [clearmlapi,clearmlfile,clearmlweb] >> Edge() >> clearmlserver 
                clearmlserver << Edge() << clearmlagent
                clearmlserver >> Edge() << clearmlserving 
                clearmlserving >> Edge() >> prometheus
                clearmlserving >> Edge() >> tritonserver
                mljob >> Edge() >> [gitlabserver,harborserver,objectstore,libraries,clearmlserver]

                #Triton internal interactions
                tritonsvc >> Edge(label="https") >> tritonserver
                [tritonserver] - Edge() - podscaler
                [tritonserver] >> Edge(label="https") >> prometheus 
                
                
                
            with Cluster("Workers"):
                k8sNodes=[Node("DGXs") - Edge(Label="", penwidth="0") - Node("GPU/CPU Servers")]    


    #Server positioning
    ordering=[gitlabserver - Edge(penwidth="0") - harborserver , objectstore - Edge(penwidth="0") - libraries - Edge(penwidth="0") - ingress]    

    #vm positioning
    vmordering=gitlabserver - Edge(penwidth="0") - harborserver - Edge(penwidth="0") - objectstore - Edge(penwidth="0") - libraries

    #Client interactions
    clients >> Edge(label="https") >> [gitlabserver, gitlabci, harborserver , objectstore , libraries ,ingress]
    clients -  Edge(penwidth="0") - labelstudio
    clients >> Edge(label="https") >> customApp

    #Staging interactions
    customApp >> Edge(label="https") << nifi
    customApp >> Edge() << kafka
    nifi >> Edge(label="https/gRPC") >> [ingress]
    nifi >> Edge() << [kafka]