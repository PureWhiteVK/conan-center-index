from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
    collect_libs,
)
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os


required_conan_version = ">=2.0.9"


class NativeFileDialogExtendedConan(ConanFile):
    name = "nativefiledialog-extended"
    description = "Cross platform (Windows, Mac, Linux) native file dialog library with C and C++ bindings, based on mlabbe/nativefiledialog."
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/btzy/nativefiledialog-extended"
    topics = ("folder-picker", "file-dialog", "cross-platform")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    # no exports_sources attribute, but export_sources(self) method instead
    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        # Keep this logic only in case configure() is needed e.g pure-c project.
        # Otherwise remove configure() and auto_shared_fpic will manage it.
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        pass
        # # Always prefer self.requirements() method instead of self.requires attribute.
        # self.requires("dependency/0.8.1")
        # if self.options.with_foobar:
        #     # INFO: used in foo/baz.hpp:34
        #     self.requires("foobar/0.1.0", transitive_headers=True, transitive_libs=True)
        # # Some dependencies on CCI are allowed to use version ranges.
        # # See https://github.com/conan-io/conan-center-index/blob/master/docs/adding_packages/dependencies.md#version-ranges
        # self.requires("openssl/[>=1.1 <4]")

    def validate(self):
        # validate the minimum cpp standard supported. For C++ projects only.
        check_min_cppstd(self, 11)

    # if a tool other than the compiler or CMake newer than 3.15 is required to build the project (pkgconf, bison, flex etc)
    def build_requirements(self):
        pass
        # self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # Using patches is always the last resort to fix issues. If possible, try to fix the issue in the upstream project.
        apply_conandata_patches(self)

    def generate(self):
        # BUILD_SHARED_LIBS and POSITION_INDEPENDENT_CODE are set automatically as tc.variables when self.options.shared or self.options.fPIC exist
        tc = CMakeToolchain(self)
        # Boolean values are preferred instead of "ON"/"OFF"
        tc.cache_variables["NFD_BUILD_TESTS"] = False
        tc.cache_variables["NFD_BUILD_SDL2_TESTS"] = False
        if is_msvc(self):
            tc.cache_variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = (
                not is_msvc_static_runtime(self)
            )
        tc.generate()

        # In case there are dependencies listed under requirements, CMakeDeps should be used
        deps = CMakeDeps(self)
        # You can override the CMake package and target names if they don't match the names used in the project
        # deps.set_property("fontconfig", "cmake_file_name", "Fontconfig")
        # deps.set_property("fontconfig", "cmake_target_name", "Fontconfig::Fontconfig")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE",
            self.source_folder,
            os.path.join(self.package_folder, "licenses"),
        )
        cmake = CMake(self)
        cmake.install()

        # Some files extensions and folders are not allowed. Please, read the FAQs to get informed.
        # Consider disabling these at first to verify that the package_info() output matches the info exported by the project.
        # rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        # rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        # rmdir(self, os.path.join(self.package_folder, "share"))
        # rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        # library name to be packaged
        self.cpp_info.libs = collect_libs(self)
        # if package provides a CMake config file (package-config.cmake or packageConfig.cmake, with package::package target, usually installed in <prefix>/lib/cmake/<package>/)
        self.cpp_info.set_property("cmake_file_name", "nfd")
        self.cpp_info.set_property("cmake_target_name", "nfd::nfd")

        if self.settings.os in ["Macos"]:
            self.cpp_info.frameworks = ["AppKit","UniformTypeIdentifiers"]
        # If they are needed on Linux, m, pthread and dl are usually needed on FreeBSD too
        # if self.settings.os in ["Linux", "FreeBSD"]:
        #     self.cpp_info.system_libs.append("m")
        #     self.cpp_info.system_libs.append("pthread")
        #     self.cpp_info.system_libs.append("dl")
