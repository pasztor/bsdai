RELVER?=	14.0
RELEASE?=	${RELVER}-RELEASE
ARCH?=		amd64
DIST?=		FreeBSD
DISTISO?=	${DIST}-${RELEASE}-${ARCH}-disc1.iso
OUTISO?=	${DIST}-${RELEASE}-${ARCH}-autoinstall.iso
INSTALLSCRIPT=	installerconfig.pre	setup_on_firstboot	installerconfig.post
DISTRIBUTIONS?=	base.txz kernel.txz
WORKDIR?=	work.${RELVER}

iso:
	mkdir -p ${WORKDIR}
	tar xvf ${DISTISO} -C ${WORKDIR}
	cat ${INSTALLSCRIPT} | sed -e 's/@DISTRIBUTIONS@/${DISTRIBUTIONS}/' >${WORKDIR}/etc/installerconfig
	rm `find ${WORKDIR}/usr/freebsd-dist -type f | egrep -v '${DISTRIBUTIONS:ts|}|MANIFEST' `
	install -m 555 -o root -g wheel rc.local ${WORKDIR}/etc/rc.local
	sh /usr/src/release/amd64/mkisoimages.sh -b '${RELVER:S/./_/}_RELEASE_AMD64_CD' ${OUTISO} ${WORKDIR}

clean:
	rm -rf ${WORKDIR}

test:
	echo 'blah ${RELVER:S/./_/}'
	printf 'asd'
	echo 'distributions: _MANIFEST|${DISTRIBUTIONS:ts|}_'
