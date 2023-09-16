pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Define the Dockerfile path
                    def dockerfilePath = "${workspace}\\Dockerfile"

                    // Define the Docker image tag
                    def dockerImageTag = "my-docker-image:latest"

                    // Build the Docker image
                    def dockerImage = docker.build(dockerImageTag, "-f ${dockerfilePath} .")

                    // Push the Docker image (if needed)
                    // dockerImage.push()
                }
            }
        }
    }
}
