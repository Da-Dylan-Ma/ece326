INSTALL_PATH=/cad2/ece326f

install: remove
	cp -R . $(INSTALL_PATH)/tester

update:
	rm $(INSTALL_PATH)/tester/bin/*
	rm -rf $(INSTALL_PATH)/tester/data
	rm -rf $(INSTALL_PATH)/tester/scripts
	cp tester/bin/* $(INSTALL_PATH)/tester/bin/
	cp -R tester/data/ $(INSTALL_PATH)/tester/data
	cp -R tester/scripts $(INSTALL_PATH)/tester/scripts

.PHONY: remove
remove:
	rm -rf $(INSTALL_PATH)/tester/
	
