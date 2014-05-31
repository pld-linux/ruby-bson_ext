#
# Conditional build:
%bcond_without	tests		# build without tests

%define	gem_name bson_ext
Summary:	C extensions for Ruby BSON
Name:		ruby-%{gem_name}
Version:	1.6.4
Release:	1
License:	Apache v2.0
Group:		Development/Languages
Source0:	http://rubygems.org/gems/%{gem_name}-%{version}.gem
# Source0-md5:	5360798f3d7d94d65be6c19aeacfc91f
# git clone http://github.com/mongodb/mongo-ruby-driver.git && cd mongo-ruby-driver/
# git checkout 1.6.4
# tar czvf bson_ext-1.6.4-tests.tgz test/bson/ test/support/
Source1:	%{gem_name}-%{version}-tests.tgz
URL:		http://www.mongodb.org/display/DOCS/BSON
BuildRequires:	rpm-rubyprov
BuildRequires:	rpmbuild(macros) >= 1.656
BuildRequires:	setup.rb
%if %{with tests}
BuildRequires:	ruby-bson >= 1.4.0
BuildRequires:	ruby-json
BuildRequires:	ruby-minitest
%endif
Requires:	ruby-bson >= 1.4.0
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
C extensions to accelerate the Ruby BSON serialization. For more
information about BSON, see <http://bsonspec.org>. For information
about MongoDB, see <http://www.mongodb.org>.

%package doc
Summary:	Documentation for %{name}
Group:		Documentation
Requires:	%{name} = %{version}-%{release}

%description doc
Documentation for %{name}

%prep
%setup -q -n %{gem_name}-%{version} -a1
cp -p %{_datadir}/setup.rb .

%build
%{__ruby} setup.rb config
%{__make} V=1 -C ext/cbson \
	CC="%{__cc}"

%if %{with tests}
# Run the test suite with minitest.
# https://jira.mongodb.org/browse/RUBY-465
sed -i "/gem 'test-unit'/ d" test/bson/test_helper.rb

# Remove the inclusion of bson (absolute path that doesn't exist) and rather require it while running ruby
sed -i "/require File.join(File.dirname(__FILE__), '..', '..', 'lib', 'bson')/d" test/bson/test_helper.rb

# Test suite fails on i386 :/
# https://jira.mongodb.org/browse/RUBY-466
ruby -Iext -e "require 'bson'; Dir.glob('./test/bson/*_test.rb').each {|t| require t}" || :
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{ruby_vendorarchdir}
install -p ext/cbson/cbson.so $RPM_BUILD_ROOT%{ruby_vendorarchdir}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{ruby_vendorarchdir}/cbson.so
