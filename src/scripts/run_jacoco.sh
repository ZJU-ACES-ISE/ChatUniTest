#!/bin/bash
# Run tests with jacoco maven plugin
# Usage: bash run_jacoco.sh <target_full_test_name>

# tests=(com.selimhorri.app.exception.wrapper.VerificationTokenNotFoundException
# com.selimhorri.app.exception.wrapper.CredentialNotFoundException
# com.selimhorri.app.business.auth.model.response.AuthenticationResponse
# com.selimhorri.app.business.auth.model.request.AuthenticationRequest
# com.selimhorri.app.business.payment.model.PaymentStatus
# com.selimhorri.app.business.product.model.response.CategoryProductServiceCollectionDtoResponse
# com.selimhorri.app.business.orderItem.model.OrderItemId
# com.selimhorri.app.business.order.model.response.OrderOrderServiceDtoCollectionResponse
# com.selimhorri.app.business.user.model.RoleBasedAuthority
# com.selimhorri.app.business.user.model.response.AddressUserServiceCollectionDtoResponse
# com.selimhorri.app.ProxyClientApplication)
tests=($1)

results=()
for t in ${tests[@]}; do
	t_name=${t##*.}
	tests_found=($(find src_test -name "${t_name}*"))
	if [ ${#tests_found} -eq 0 ]; then
		continue
	fi
	targets=($(find . -name ${t_name}.java))
	targets=${targets%/com/*}
	echo $tests_found
	echo $targets
	sleep 3
	for target in ${targets[@]}; do
		for tf in ${tests_found[@]}; do
			target=$(echo $target | sed 's/main/test/')
			cp $tf $target
		done
		module=$(echo $target | cut -d'/' -f2)
		mvn clean test org.jacoco:jacoco-maven-plugin:prepare-agent install -DfailIfNoTests=false -Dmaven.compiler.failOnError=false -pl $module
		mvn org.jacoco:jacoco-maven-plugin:report
		results+=(`cat ${module}/target/jacoco-report/jacoco.csv | grep $t_name`)
	done
done

for e in ${results[@]}; do
	echo -e "$e\n"
done
