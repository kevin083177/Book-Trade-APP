import { Product } from "../interface/Product";

export type RootStackParamList = {
    Auth: undefined; //登入/註冊系統頁面 (最外層)
    Main: undefined; //主畫面連接底部導瀏覽
};
export type MainTabParamList = {
    Cart: undefined;
    Chat: undefined;
    Home: undefined;
    Notification: undefined;
    Profile: undefined;
}
export type AuthStackParamList = {
    Login: undefined;
    Register: undefined;
    Loading: undefined;
    Forget: undefined;
}
export type HomeStackParamList = {
    Index: undefined;
    Product: { productId: string, source: String};
}
export type CartStackParamList = {
    Index: undefined;
    Checkout: {productId: number[]}
}
export type ProfileStackParamList = {
    Index: undefined;
    Setting: undefined;
    Collection: undefined;
    Pending: undefined;
    Completed: undefined;
    Evaluate: undefined;
    Seller: {product?: Product};
    Edit: undefined;
    Report: undefined;
}
export type ChatStackParamList = {
    Index: undefined;
}