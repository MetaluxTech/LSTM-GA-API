from flask import Flask, request, jsonify
import random
import numpy as np
from tensorflow import keras

app = Flask(__name__)

# Load the trained LSTM model
loaded_lstm_model = keras.models.load_model('saved_lstm_model.h5')

# Define a function to predict resource requirements using the loaded LSTM model
def predict_resource_requirements(datacenter):
    # Extract resource values from the dictionary
    cpu_cores = datacenter['Available Resources']['CPUCores']
    memory_gb = datacenter['Available Resources']['MemoryGB']
    cost = datacenter['Cost']
    
    # Create an input array with the extracted values
    input_data = np.array([[cpu_cores, memory_gb, cost]])
    
    predicted_output = loaded_lstm_model.predict(input_data)
    return predicted_output

# Define an example Genetic Algorithm (GA) function for optimization
def genetic_algorithm(datacenters, generations, budget):
    best_datacenter = None
    best_cost = float('inf')
    sla_threshold = 0.1  # Define an SLA compliance threshold

    for _ in range(generations):
        # Randomly select a datacenter from the list
        selected_datacenter = random.choice(datacenters)

        # Use LSTM to predict future resource requirements for the selected datacenter
        predicted_requirements = predict_resource_requirements(selected_datacenter)

        # Calculate fitness based on multiple factors (latency, resources, cost, SLA)
        latency_fitness = selected_datacenter['Latency']
        resources_fitness = 1 / (selected_datacenter['Available Resources']['CPUCores'] + 1e-5)  # Avoid division by zero
        cost_fitness = selected_datacenter['Cost']

        # SLA compliance (example, if Response Time exceeds a threshold)
        response_time = predicted_requirements[0][0]  # Assuming the first element is Response Time
        sla_penalty = max(0, response_time - sla_threshold)  # Penalize SLA violations

        # Combine fitness factors and SLA penalty into the overall fitness
        fitness = latency_fitness + resources_fitness + cost_fitness + sla_penalty

        # Check if the datacenter fits within the budget
        if selected_datacenter['Cost'] <= budget:
            # Update the best choice if the fitness is better
            if fitness < best_cost:
                best_cost = selected_datacenter['Cost']
                best_datacenter = selected_datacenter

    return best_datacenter


@app.route('/optimize', methods=['POST'])
def optimize_datacenter():
    
    try:
        request_data = request.get_json()
        input_budget = request_data['budget_value']
        input_budget=int(input_budget)
        # input_budget = 2000

        # Run the Genetic Algorithm with the specified budget constraint
        best_datacenter = genetic_algorithm(datacenters, generations=100, budget=input_budget)

        if best_datacenter:
            return jsonify({'message': 'Success', 'best_datacenter': best_datacenter}), 200
        else:
            return jsonify({'message': 'No suitable datacenter found within the budget'}), 404

    except Exception as e:
            print('error::' ,jsonify({'error': str(e)}))
            return jsonify({'error': str(e)}), 444

if __name__ == '__main__':
    # Example list of datacenters with realistic specifications
    datacenters = [
        {
            'Name': 'Datacenter A',
            'Latency': 120,
            'Available Resources': {'CPUCores': 12, 'MemoryGB': 2048, 'StorageTB': 10, 'NetworkBandwidthGbps': 10},
            'Cost': 1000,
        },
        {
            'Name': 'Datacenter B',
            'Latency': 300,
            'Available Resources': {'CPUCores': 11, 'MemoryGB': 2148, 'StorageTB': 11, 'NetworkBandwidthGbps': 11},
            'Cost': 2000,
        },
        {
            'Name': 'Datacenter C',
            'Latency': 50,
            'Available Resources': {'CPUCores': 20, 'MemoryGB': 2248, 'StorageTB': 12, 'NetworkBandwidthGbps': 12},
            'Cost': 3000,
        }
        # Add more datacenters with realistic specifications
    ]

    app.run(debug=True)