#!/usr/bin/env python

import rospy
import tf
from geometry_msgs.msg import PoseStamped

if __name__ == '__main__':
    rospy.init_node('publish_pose', anonymous=True)
    worldFrame = rospy.get_param("~worldFrame", "/world")
    name = rospy.get_param("~name")     # publish to
    r = rospy.get_param("~rate","50")	# frequency
    x = rospy.get_param("~x","0.2")	# meter
    y = rospy.get_param("~y","0.2")	# meter
    z = rospy.get_param("~z","0.8")	# meter
    yaw = rospy.get_param("~yaw","0") 	# radian

    rate = rospy.Rate(r)
 
    msg = PoseStamped()
    msg.header.seq = 0
    msg.header.stamp = rospy.Time.now()
    #start_time = rospy.Time()
    #start_time = msg.header.stamp
    msg.header.frame_id = worldFrame
    msg.pose.position.x = x
    msg.pose.position.y = y
    msg.pose.position.z = z
    quaternion = tf.transformations.quaternion_from_euler(0, 0, yaw)
    msg.pose.orientation.x = quaternion[0]
    msg.pose.orientation.y = quaternion[1]
    msg.pose.orientation.z = quaternion[2]
    msg.pose.orientation.w = quaternion[3]

    pub = rospy.Publisher(name, PoseStamped, queue_size=1)

    while not rospy.is_shutdown():
        msg.header.seq += 1
        msg.header.stamp = rospy.Time.now()
	#rospy.loginfo("goal time: %f", msg.header.stamp.to_sec() - start_time.to_sec())
        pub.publish(msg)
        rate.sleep()
