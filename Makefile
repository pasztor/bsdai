RELVER?=	13.1
RELEASE?=	${RELVER}-RELEASE
ARCH?=		amd64
DIST?=		FreeBSD
DISTISO?=	${DIST}-${RELEASE}-${ARCH}-disc1.iso
OUTISO?=	${DIST}-${RELEASE}-${ARCH}-autoinstall.iso
INSTALLSCRIPT=	installerconfig.pre	setup_on_firstboot	installerconfig.post
DISTRIBUTIONS?=	base.txz kernel.txz

iso:
	mkdir -p work
	tar xvf ${DISTISO} -C work
	cat ${INSTALLSCRIPT} | sed -e 's/@DISTRIBUTIONS@/${DISTRIBUTIONS}/' >work/etc/installerconfig
	rm `find work/usr/freebsd-dist -type f | egrep -v '${DISTRIBUTIONS:ts|}|MANIFEST' `
	cat ed_rc.local | ed work/etc/rc.local
	sh /usr/src/release/amd64/mkisoimages.sh -b '${RELVER:S/./_/}_RELEASE_AMD64_CD' ${OUTISO} work

clean:
	rm -rf work

test:
	echo 'blah ${RELVER:S/./_/}'
	printf 'asd'
	echo 'distributions: _MANIFEST|${DISTRIBUTIONS:ts|}_'
