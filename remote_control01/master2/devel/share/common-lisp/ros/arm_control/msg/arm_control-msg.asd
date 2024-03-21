
(cl:in-package :asdf)

(defsystem "arm_control-msg"
  :depends-on (:roslisp-msg-protocol :roslisp-utils )
  :components ((:file "_package")
    (:file "JointControl" :depends-on ("_package_JointControl"))
    (:file "_package_JointControl" :depends-on ("_package"))
    (:file "JointInformation" :depends-on ("_package_JointInformation"))
    (:file "_package_JointInformation" :depends-on ("_package"))
    (:file "PosCmd" :depends-on ("_package_PosCmd"))
    (:file "_package_PosCmd" :depends-on ("_package"))
  ))