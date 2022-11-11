pipeline {
    agent any

    stages {
	    stage('Down-stream') {
		
		   steps {
		      
		     script {
			 
			   sh script:'''
                    #!/bin/bash
                    
                        echo "Starting the Slave test Job ::"
                    
                '''  
                i=0
                
                while (i<2){
                
                 build propagate: false, job: 'testjob'
                 i = i + 2
              }
			 
			 }
		   }
		
		}
    }
}

kubectl create ns jenkins
kubectl get ns
kubectl config view | grep namespace
kubectl config set-context --current --namespace=jenkins
kubectl apply -f .
kubectl exec -it jenkins-master-deployment-5d8558b578-hjdjr -- /bin/bash
kubectl cluster-info
kubectl get svc
kubectl create clusterrolebinding permissive-binding --clusterrole=cluster-admin --user=admin --user=kubelet --group=system:serviceaccounts