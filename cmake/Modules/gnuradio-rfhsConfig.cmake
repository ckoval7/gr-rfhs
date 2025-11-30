find_package(PkgConfig)

PKG_CHECK_MODULES(PC_GR_RFHS gnuradio-rfhs)

FIND_PATH(
    GR_RFHS_INCLUDE_DIRS
    NAMES gnuradio/rfhs/api.h
    HINTS $ENV{RFHS_DIR}/include
        ${PC_RFHS_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    GR_RFHS_LIBRARIES
    NAMES gnuradio-rfhs
    HINTS $ENV{RFHS_DIR}/lib
        ${PC_RFHS_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/gnuradio-rfhsTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(GR_RFHS DEFAULT_MSG GR_RFHS_LIBRARIES GR_RFHS_INCLUDE_DIRS)
MARK_AS_ADVANCED(GR_RFHS_LIBRARIES GR_RFHS_INCLUDE_DIRS)
