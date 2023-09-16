pipeline {
    agent any
    stages {
        stage('Build Docker Image') {
            steps {
                script {
                    // Define the path to your Dockerfile
                    def dockerfilePath = "/Users/hoanguyen/.jenkins/workspace/multi-branch_dev-h/Dockerfile"
                    
                    // Build the Docker image with the correct Dockerfile path
                    sh "docker build -t my-docker-image:latest -f ${dockerfilePath} ."
                }
            }
        }
        // Add other stages as needed
    }
}

