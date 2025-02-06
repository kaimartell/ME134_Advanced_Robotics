def isTooClose(adc_value):
    #10 bit ADC, 3.3V reference voltage
    voltage = (adc_value / 1023) * 3.3
    
    #according to graph, 0.75 is the output voltage at 35cm away
    threshold_voltage = 0.75 

    return voltage > threshold_voltage #true if too close
