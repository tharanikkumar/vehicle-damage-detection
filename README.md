LLM infused Vehicle Damage Detection and Repair Cost Estimation System

1. Introduction

   Vehicle damage detection and cost estimation is a crucial application of AI in the automotive industry. This project utilizes computer vision and deep learning to analyze vehicle images, detect damages, and estimate repair costs based on the extent and type of damage.

2. Problem Statement

   Manual vehicle damage inspection is time-consuming and prone to errors. Traditional assessment methods require human intervention, leading to inconsistencies and potential bias. Automating this process can improve accuracy, efficiency, and cost estimation precision.

3. Proposed Solution

   The proposed solution uses a deep learning-based approach for vehicle damage detection and cost estimation. It involves image classification, damage segmentation, and a cost estimation model trained on real-world data. The system employs convolutional neural networks (CNNs) and Gemini AI for accurate predictions.

4. Use Case

   The AI-powered vehicle damage detection and cost estimation system is designed to automate the assessment of vehicle damages and provide accurate repair cost estimates. This system utilizes advanced computer vision techniques, deep learning models, and large language models (LLMs) to analyze images of damaged vehicles, classify different types of damage, and generate repair cost estimations. The solution benefits various stakeholders, including vehicle owners, insurance companies, repair service providers, automobile manufacturers, and fleet management companies. Vehicle owners can assess damages and estimate repair costs without visiting a service center, while insurance companies can streamline claim approvals and prevent fraud. Repair centers and garages can use the system to standardize damage assessment and pricing, ensuring fair and transparent costs.
The process begins when the user uploads an image of a damaged vehicle through a web or mobile application. The system first verifies whether the uploaded image is a car. If the image is not a vehicle, it notifies the user to upload a valid car image. Once the system confirms the image is a vehicle, it applies Mask R-CNN with a ResNet-101 backbone and Deformable Convolution Networks to detect damaged areas. It then classifies damages into different categories such as dents, scratches, cracks, shattered glass, broken lamps, or flat tires. If no damage is detected, the system displays a message indicating that the vehicle is in good condition. For damaged vehicles, the system further assesses the severity, categorizing it into minor, moderate, or severe damage. Minor damages include surface scratches or small dents, moderate damages involve larger dents and broken parts, while severe damages consist of structural damage or extensive breakage.

5. System Overview

   The Vehicle Damage Detection and Cost Estimation system consists of three main components:
   
   Frontend: A user-friendly interface built using Streamlit, allowing users to upload car images and view results.

   Backend: A Flask-based API handling image processing, damage detection, and cost estimation.

   Database: A MySQL database storing image metadata, detection results, and historical repair cost data.

6. Workflow
   
   Image Upload: Users upload a car image through the web interface.

   Preprocessing: The backend verifies if the image is of a vehicle.

   Damage Detection: The image undergoes analysis using Mask R-CNN with a ResNet-101 backbone and deformable convolution networks.

   Damage Classification: Detected damage is classified into different categories.

   Cost Estimation: The repair cost is predicted using AI-based analysis and market data.

   Result Display: The system returns a marked image with identified damage and estimated cost.

7. Modules

   A. Backend Modules (Flask & Python)
   

   User Authentication Module: Handles user registration, login, JWT authentication, and role-based access control.


   Image Processing Module: Preprocesses images, including resizing, noise reduction, and enhancement.


   Vehicle Detection Module: Classifies whether the uploaded image is a car or not.


   Damage Detection Module: Uses Mask R-CNN to detect and classify damages.


   Severity Classification Module: Categorizes damage into minor, moderate, or severe.


   Cost Estimation Module: Uses an LLM model and Google API to estimate repair costs based on damage severity.


   Report Generation Module: Generates downloadable reports containing detected damages and cost estimates.


   B. Frontend Modules (React.js & Tailwind CSS)


   User Dashboard: Displays uploaded images, damage analysis, and cost estimation results.


   Image Upload Component: Allows users to upload car accident images.


   Result Display Component: Shows marked damage areas and repair costs.


   Report Download Component: Provides options to download or share the generated report.


   C. Database Modules (MySQL)


   User Table: Stores user credentials, roles, and authentication tokens.


   Uploaded Images Table: Keeps a record of uploaded images.


   Damage Detection Results Table: Stores damage classification and severity details.


   Cost Estimation Table: Saves estimated repair costs for future reference.


8. Alignment with SDG goals


   SDG 3 – Good Health and Well-Being

   SDG 9 – Industry, Innovation, and Infrastructure

   SDG 11 – Sustainable Cities and Communities

   SDG 12 – Responsible Consumption and Production

   SDG 13 – Climate Action


9. Expected Outcomes

    
   Automated Damage Assessment: Faster and more accurate detection of vehicle damages.
   
   Reliable Cost Estimation: AI-based cost predictions reducing manual estimation errors.
   
   Improved Insurance Processing: Faster claims assessment for insurers.
   
   User-Friendly Interface: A simple web-based tool for vehicle owners and mechanics.


10. Dependecies and Requirements


   - Python 3.9+
   - TensorFlow / PyTorch
   - OpenCV for image processing
   - Flask for backend API development
   - Streamlit for UI visualization
   - MySQL for data storage
   - Google API for cost estimation based on car brand and damage severity.


11. MySQL Database connection(available in the name "schema.sql")


        CREATE DATABASE IF NOT EXISTS vehicle_damage;

        USE vehicle_damage;

        CREATE TABLE IF NOT EXISTS damage_reports (
            id INT AUTO_INCREMENT PRIMARY KEY,
            image_path VARCHAR(255) NOT NULL,
            damage_result TEXT NOT NULL,
            cost_estimation VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );



12. Running the Project (Use New terminal for each module):


    Streamlit UI:

        cd streamlit
    
        pip install -r requirements.txt

    Backend (Flask):

        cd backend
    
        pip install -r requirements.txt
    
        python app.py

    Frontend:

        cd frontend

        streamlit run app.py

13. Output Screenshots

        
<img width="1440" alt="s1" src="https://github.com/user-attachments/assets/79d4ca98-32e0-4daa-ba3d-51c3cff6065f" />

<img width="1440" alt="s2" src="https://github.com/user-attachments/assets/51a38e03-eacc-4256-80e9-631d0cbda9f8" />

<img width="1440" alt="s3" src="https://github.com/user-attachments/assets/5e020fb9-3347-4247-a70e-6185e14304dd" />

<img width="1440" alt="s4" src="https://github.com/user-attachments/assets/31fe1b7b-ff38-4154-8357-cab2140b11ca" />

<img width="1440" alt="s5" src="https://github.com/user-attachments/assets/5520b292-cb59-4fed-9c81-0ddb7e9d59c1" />

<img width="1440" alt="s6" src="https://github.com/user-attachments/assets/508f6a74-f35e-4265-8996-0ea04a237c4d" />










   
