#include <bcm2835.h>

// GPIO pin 9
#define nPL RPI_GPIO_P1_21
// GPIO pin 10
#define Q7 RPI_GPIO_P1_19
// GPIO pin 11
#define CP RPI_GPIO_P1_23

uint32_t shift_in (){
	bcm2835_init();
	bcm2835_gpio_fsel(nPL, BCM2835_GPIO_FSEL_OUTP);
	bcm2835_gpio_fsel(Q7, BCM2835_GPIO_FSEL_INPT);
	bcm2835_gpio_fsel(CP, BCM2835_GPIO_FSEL_OUTP);
	
	bcm2835_gpio_write(CP, LOW); // rising edge triggered
	
	bcm2835_gpio_write(nPL, LOW); // load the current values
	bcm2835_gpio_write(nPL, HIGH); // keep them while we shift
		
	uint32_t out = 0;
	for(int i=0; i<32; ++i){
		bcm2835_gpio_write(CP, HIGH);
		out |= (uint32_t) bcm2835_gpio_lev(Q7) << i;
		bcm2835_gpio_write(CP, LOW);
	}
	
	bcm2835_gpio_write(nPL, LOW); // listen for new values
	
	bcm2835_close();
	return out;
}