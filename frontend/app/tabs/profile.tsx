import { View, Text, TouchableOpacity, Alert, Image } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation, NavigationProp, useFocusEffect } from '@react-navigation/native';
import { clearUserData } from '@/utils/stroage';
import { api } from '@/api/api';
import { asyncGet } from '@/utils/fetch';
import { getUserId } from '@/utils/stroage';
import { useState } from 'react';
import { styles } from './styles/profile';
import React from 'react';
export default function ProfileScreen() {
  const navigation = useNavigation<NavigationProp<any>>();
  const [userName, setUserName] = useState<string | null>();
  const [evaluate, setEvaluate] = useState<number>(0.0);
  const [transaction, setTransaction] = useState<number>();
  const [photouri, setPhotoUri] = useState<string>("");
  const fetchUserInformation = async () => {
    try {
      const id = await getUserId();
      const user = await asyncGet(`${api.find}?_id=${id}`);
      setUserName(user.body.username);
      setEvaluate(user.body.evaluate);
      setTransaction(user.body.transaction_number);
      setPhotoUri(user.body.headshot);
    } catch (error) {
      console.error("Failed to fetch user information:", error);
    }
  };

  useFocusEffect(
    React.useCallback(() => {
      // 當頁面獲得焦點時執行
      fetchUserInformation();
    }, [])
  );

  const handle_logout = async () => {
    const logout_response = await clearUserData();
    if (logout_response) {
      navigation.navigate("Auth");
    } else {
      Alert.alert("伺服器發生錯誤");
    }
  };
  return (
    <SafeAreaView style={styles.container}>
        <View style={styles.logoContainer}>
          <Text style={styles.logoText}>二手書交易平台</Text>
        </View>
      {/* Header Section */}
      <View style={styles.headerContainer}>
        <View style={styles.profileContainer}>
          {photouri
          ?
            <Image source={{uri: photouri}} style={styles.image}/>
          : 
            <Ionicons name="person-circle-outline" size={80} color="black" />
          }
          <View style={styles.profileInfo}>
            <Text style={styles.userId}>{userName ? userName : "Loading..."}</Text>
            <Text style={styles.rating}>{evaluate ? `⭐ ${evaluate} (${transaction})` : "⭐您尚未擁有評價"}</Text>
          </View>
        </View>
        <TouchableOpacity style={styles.headerIcons} onPress={() => navigation.navigate('Setting')}>
          <Ionicons name="settings-outline" size={24} color="black" style={styles.icon} />
        </TouchableOpacity>
      </View>

      {/* Buttons Section */}
      <View style={styles.buttonsRow}>
        <TouchableOpacity style={styles.buttonWrapper} onPress={() => navigation.navigate('OrderStatus', {status: "待確認"})}>
          <Ionicons name="time-outline" size={28} color="black" />
          <Text style={styles.buttonText}>待確認</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.buttonWrapper} onPress={() => navigation.navigate('OrderStatus', { status: "待處理" })}>
          <Ionicons name="swap-horizontal-outline" size={28} color="black" />
          <Text style={styles.buttonText}>待交易</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.buttonWrapper} onPress={() => navigation.navigate('OrderStatus', { status: "待評價" })}>
          <Ionicons name="star-outline" size={28} color="black" />
          <Text style={styles.buttonText}>待評價</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.buttonWrapper} onPress={() => navigation.navigate('OrderStatus', { status: "已完成" })}>
          <Ionicons name="checkmark-done-outline" size={28} color="black" />
          <Text style={styles.buttonText}>已完成</Text>
        </TouchableOpacity>
      </View>

      {/* Options Section */}
      <View style={styles.optionsContainer}>
      <TouchableOpacity style={styles.optionRow} onPress={() => {navigation.navigate('Favorite')}}>
          <Ionicons name="bookmark-outline" size={24} color="black" style={styles.optionIcon} />
          <Text style={styles.optionText}>收藏庫</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.optionRow} onPress={() => {navigation.navigate('Seller')}}>
          <Ionicons name="cloud-upload-outline" size={24} color="black" style={styles.optionIcon} />
          <Text style={styles.optionText}>刊登新商品</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.optionRow} onPress={() => navigation.navigate('Edit')}>
          <Ionicons name="create-outline" size={24} color="black" style={styles.optionIcon} />
          <Text style={styles.optionText}>修改已發佈商品</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.optionRow} onPress={() => navigation.navigate('Report')}>
          <Ionicons name="mail-outline" size={24} color="black" style={styles.optionIcon} />
          <Text style={styles.optionText}>功能建議與問題回報</Text>
        </TouchableOpacity>
      </View>

      {/* Footer Section */}
      <TouchableOpacity style={styles.footerContainer} onPress={() => handle_logout()}>
        <Ionicons name="log-out-outline" size={24} color="red" />
        <Text style={styles.footerText}>登出</Text>
      </TouchableOpacity>
    </SafeAreaView>
  );
}