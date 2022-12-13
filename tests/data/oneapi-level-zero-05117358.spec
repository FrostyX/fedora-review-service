%global         srcname level-zero
Name:		oneapi-%{srcname}
Version:    	1.8.8
Release:    	%{autorelease}
Summary:    	OneAPI Level Zero Specification Headers and Loader

License:    	MIT
URL:        	https://github.com/oneapi-src/%{srcname}
Source:	        %{url}/archive/v%{version}.tar.gz#/%{srcname}-%{version}.tar.gz

ExclusiveArch:	x86_64

BuildRequires:	gcc-c++
BuildRequires:	cmake
BuildRequires:	make
BuildRequires:	opencl-headers

%description
The objective of the oneAPI Level-Zero Application Programming Interface
(API) is to provide direct-to-metal interfaces to offload accelerator
devices. Its programming interface can be tailored to any device needs
and can be adapted to support broader set of languages features such as
function pointers, virtual functions, unified memory,
and I/O capabilities.

%package	devel
Summary:        The oneAPI Level Zero Specification Headers and Loader development package
Requires:       %{name} = %{version}-%{release}

%description    devel
The %{name}-devel package contains library and header files for
developing applications that use %{name}.

%prep
%autosetup -n %{srcname}-%{version}

%build
%cmake
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md SECURITY.md
%{_libdir}/libze_loader.so.1*
%{_libdir}/libze_validation_layer.so.1*
%{_libdir}/libze_tracing_layer.so.1*

%files devel
%{_includedir}/level_zero
%{_libdir}/libze_loader.so
%{_libdir}/libze_validation_layer.so
%{_libdir}/libze_tracing_layer.so
%{_libdir}/pkgconfig/libze_loader.pc
%{_libdir}/pkgconfig/%{srcname}.pc

%changelog
%autochangelog
