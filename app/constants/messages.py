"""
Message Templates and Text Constants
Centralized message management for consistency and easy localization
"""


class WelcomeMessages:
    """Welcome and greeting messages"""
    MAIN_WELCOME = (
        "سلام دوست خوبم👋\n"
        "🤖به ربات ماز خوش اومدی🤖\n\n"
        "من اینجام تا مرحله به مرحله در خصوص محصولات، مشاوره و شرایط اقساطی "
        "نمایندگی ماز راهنماییت کنم🦾\n\n"
        "🔻از منوی زیر بخش مورد نظرت رو انتخاب کن تا به امکانات من دسترسی داشته باشی😉"
    )
    
    RETURN_TO_MENU = (
        "سلام دوست خوبم👋\n"
        "🤖به ربات ماز خوش اومدی🤖\n\n"
        "من اینجام تا مرحله به مرحله در خصوص محصولات، مشاوره و شرایط اقساطی "
        "نمایندگی ماز راهنماییت کنم🦾\n\n"
        "/start رو برای دیدن منو بزنید"
    )


class RegistrationMessages:
    """User registration related messages"""
    ASK_NAME = "👤 لطفاً نام و نام خانوادگی خود را به فارسی وارد کنید:\nانصراف : /cancel"
    ASK_CITY = "👤 لطفاً شهر خود را انتخاب کنید:\n انصراف : /cancel"
    ASK_AREA = "منطقه تحصیلی خود را به عدد وارد کنید(مثال: 1یا 2 یا 3)"
    ASK_ID = "حالا کد ملی خود را وارد کنید(مثال: 1234567890)"
    ASK_PHONE = "حالا شماره موبایل خود را وارد کنید(مثال: 09123456789)"
    ASK_OTP = "✅ کد تایید پیامک شد. لطفاً کد را وارد کنید:"
    
    ALREADY_REGISTERED = "شما قبلاً ثبت‌نام کردید ✅"
    REGISTRATION_SUCCESS = "🎉 ثبت‌نام شما با موفقیت انجام شد!"
    REGISTRATION_CANCELED = "ثبت‌نام لغو شد."
    
    # Validation error messages
    INVALID_NAME = "❌ لطفاً نام و نام خانوادگی را به‌درستی و به زبان فارسی وارد کنید."
    INVALID_CITY = "❌ شهر وارد شده معتبر نیست. لطفاً شهر را به صورت صحیح وارد کنید."
    INVALID_AREA = "❌ منطقه وارد شده معتبر نیست. لطفاً منطقه را به صورت صحیح وارد کنید."
    INVALID_ID = "❌ کد ملی وارد شده معتبر نیست. لطفاً کد ملی را به صورت صحیح وارد کنید."
    INVALID_PHONE = "❌ شماره وارد شده معتبر نیست. لطفاً شماره را به صورت صحیح وارد کنید."
    INVALID_OTP = "❌ کد وارد شده صحیح نیست. لطفا فرآیند ثبت نام را از اول انجام دهید دوباره تلاش کنید:"


class ProductMessages:
    """Product and purchase related messages"""
    NOT_REGISTERED = "شما هنوز ثبت نام نکردید برای خرید نیاز است که ابتدا ثبت نام کنید"
    ASK_REFERRAL_CODE = "کد معرف دارید؟"
    ENTER_REFERRAL_CODE = "لطفا کد معرف خود را وارد کنید:"
    INVALID_REFERRAL_CODE = "کد معرف معتبر نیست. لطفا دوباره تلاش کنید:"
    SELECT_PAYMENT_METHOD = "نوع پرداخت خود را انتخاب کنید:"
    SEND_PAYMENT_PROOF = "📸 لطفا اسکرین‌شات رسید واریزی را ارسال کنید.\n\n انصراف: /start"
    
    INSTALLMENT_OPTION_UNAVAILABLE = (
        "کد معرف شما قابلیت پرداخت قسطی ندارد. لطفاً پرداخت نقدی را انتخاب کنید:"
    )
    
    ORDER_SUCCESS = "✅ سفارش شما ثبت شد. بسته شما تا ساعاتی دیگر ارسال خواهد شد.\n\n بازگشت به منو: /start"
    
    GRADE_SELECTION = "برای دیدن محصولات پایه تحصیلی مورد نظر خود را انتخاب کنید:"
    MAJOR_SELECTION = "برای انتخاب رشته مورد نظر خود را انتخاب کنید:"
    PRODUCT_SELECTION = "برای دیدن جزییات و خرید روی محصول مورد نظر کلیک کنید:"
    
    NO_PRODUCTS_FOUND = "محصولی برای این پایه و رشته یافت نشد"
    PRODUCT_NOT_FOUND = "محصول مورد نظر یافت نشد"


class AlmasSubscriptionMessages:
    """Almas subscription specific messages"""
    ALMAS_DESCRIPTION = (
        "💎اشتراک الماس رو فقط از طریق نمایندگی تهران میتونی اقساطی تهیه کنی‼️\n\n"
        "🎯دسترسی کامل به خدمات ماز تا روز کنکور \n"
        "💰پرداخت چند مرحله ای بدون بهره \n"
        "🎉دسترسی به خدمات تکمیلی نمایندگی\n\n"
        "🔻برای ادامه پایه تحصیلی خودتو انتخاب کن"
    )


class InstallmentMessages:
    """Installment related messages"""
    NO_INSTALLMENTS = "شما هیچ خرید قسطی ثبت نکرده‌اید."
    SELECT_PRODUCT = "🔻 یک محصول را انتخاب کنید تا اقساط آن را ببینید:"
    UPLOAD_RECEIPT = "📸 لطفاً رسید قسط {} را ارسال کنید."
    RECEIPT_UPLOADED = "✅ رسید قسط {} با موفقیت ثبت شد."
    ORDER_NOT_FOUND = "سفارش مورد نظر یافت نشد."
    PRODUCT_NOT_FOUND_INSTALLMENT = "محصول یافت نشد."


class CRMMessages:
    """CRM and consultation related messages"""
    ASK_PHONE = "📱 لطفاً شماره موبایل خود را برای مشاوره تلفنی رایگان وارد کنید (مثال: 09123456789):\nانصراف : /cancel"
    ASK_OTP_CRM = "✅ کد تایید پیامک شد. لطفاً کد را وارد کنید:"
    CRM_SUCCESS = "✅ اطلاعات شما با موفقیت ثبت شد! مشاوران ما در اسرع وقت با شما تماس خواهند گرفت."
    INVALID_OTP_CRM = "❌ کد وارد شده صحیح نیست. دوباره تلاش کنید:"
    
    NOT_SURE_GUIDANCE = (
        "👈بهت پیشنهاد میکنم برای راهنمایی کامل تر و رفع ابهامات با مشاورین مجموعه ما "
        "در ارتباط باشی🌹\n\nکافیه شماره تماست رو برامون ارسال کنی تا در اولین فرصت باهات تماس بگیریم☎️"
    )


class CooperationMessages:
    """Cooperation application related messages"""
    COOPERATION_INTRO = (
        "🤝 همکاری با نمایندگی ماز\n\n"
        "🌟 ما همیشه به دنبال افراد با انگیزه و متخصص هستیم\n\n"
        "📱 لطفاً شماره موبایل خود را وارد کنید (مثال: 09123456789):\n\n"
        "انصراف: /cancel"
    )
    
    ASK_OTP_COOPERATION = "✅ شماره تلفن شما تایید شد!\n\n🏙️ حالا لطفاً شهر محل سکونت خود را وارد کنید:"
    ASK_CITY_COOPERATION = "❌ لطفاً نام شهر را به درستی وارد کنید:"
    CITY_REGISTERED = "✅ شهر شما ثبت شد!"
    
    ASK_RESUME = (
        "حالا لطفا موارد زیر را به صورت متنی ارسال کنید:\n"
        "• نام و نام خانوادگی\n"
        "• سن\n"
        "• تحصیلات\n"
        "• مهارت‌ها و تخصص‌ها\n"
        "• سوابق کاری"
    )
    
    RESUME_TOO_SHORT = (
        "❌ رزومه شما خیلی کوتاه است. لطفاً اطلاعات بیشتری در مورد خودتان ارائه دهید:\n"
        "(حداقل 50 کاراکتر)"
    )
    
    TEXT_ONLY_RESUME = (
        "❌ لطفاً رزومه خود را فقط به صورت متن ارسال کنید، نه فایل یا عکس.\n"
        "📝 رزومه خود را تایپ کنید:"
    )
    
    COOPERATION_SUCCESS = (
        "✅ رزومه شما با موفقیت ثبت شد!\n\n"
        "🔍 تیم ما رزومه شما را بررسی خواهد کرد\n"
        "📞 در صورت تایید، در اسرع وقت با شما تماس خواهیم گرفت\n\n"
        "🙏 از علاقه شما به همکاری با ما متشکریم\n\n"
        "بازگشت به منو: /start"
    )
    
    COOPERATION_UPDATE_SUCCESS = (
        "✅ رزومه شما با موفقیت به‌روزرسانی شد!\n\n"
        "🔍 تیم ما رزومه جدید شما را بررسی خواهد کرد\n"
        "📞 در صورت تایید، در اسرع وقت با شما تماس خواهیم گرفت\n\n"
        "🙏 از علاقه شما به همکاری با ما متشکریم\n\n"
        "بازگشت به منو: /start"
    )


class LotteryMessages:
    """Lottery related messages"""
    NO_LOTTERY_ACTIVE = "در حال حاضر قرعه‌کشی فعالی وجود ندارد."
    SELECT_LOTTERY = "🎲 لطفا قرعه کشی مورد نظر خود را انتخاب کنید:\n\nانصراف: /cancel"
    LOTTERY_NOT_FOUND = "❌ قرعه کشی مورد نظر یافت نشد. لطفا دوباره انتخاب کنید:"
    ALREADY_REGISTERED = "✅ شما قبلاً در قرعه‌کشی '{}' ثبت‌نام کرده‌اید!\n\n📋 توضیحات: {}\n\nبازگشت به منو: /start"
    
    ASK_PHONE_LOTTERY = (
        "🎲 قرعه‌کشی انتخابی: {}\n"
        "📋 توضیحات: {}\n\n"
        "📱 لطفاً شماره موبایل خود را برای شرکت در قرعه‌کشی وارد کنید (مثال: 09123456789):\n\n"
        "انصراف: /cancel"
    )
    
    ASK_OTP_LOTTERY = "✅ کد تایید پیامک شد. لطفاً کد را وارد کنید:"
    INVALID_OTP_LOTTERY = "❌ کد وارد شده صحیح نیست. لطفا دوباره تلاش کنید:"
    
    LOTTERY_SUCCESS = (
        "🎉 تبریک! شما با موفقیت در قرعه‌کشی '{}' ثبت‌نام شدید!\n\n"
        "📱 شماره ثبت شده: {}\n"
        "🎲 قرعه‌کشی: {}\n\n"
        "🍀 موفق باشید!\n\n"
        "بازگشت به منو: /start"
    )


class ErrorMessages:
    """Error and system messages"""
    GENERAL_ERROR = "ببخشید نفهمیدم به چی نیاز داری! لطفا یکی از گزینه های منو رو انتخاب کنید."
    SMS_ERROR = "خطا در ارسال پیامک: {}"
    PAYMENT_ERROR = "❌ خطا: اطلاعات سفارش ناقص است."
    INVALID_INPUT = "❌ لطفا یکی از گزینه‌های معتبر را انتخاب کنید."
    USER_NOT_FOUND = "کاربر یافت نشد."
    PROCESSING_ERROR = "❌ خطا در پردازش درخواست."
    UPLOAD_IMAGE_ONLY = "لطفاً یک عکس از فیش واریزی ارسال کنید."
    
    MISSING_PRODUCT_INFO = "❌ خطا: اطلاعات محصول یافت نشد."
    ORDER_DATA_INCOMPLETE = "❌ خطا: اطلاعات سفارش ناقص است."


class ContactMessages:
    """Contact and help messages"""
    CONTACT_INFO = "برای ارتباط با ما و پشتیبانی میتونید به آیدی @Arshya_Alaee پیام بدید😊"
    
    HELP_TEXT = """📚 راهنمای استفاده از ربات:

🛒 نحوه خرید:
1. روی "📚 محصولات" کلیک کنید
2. پایه تحصیلی خود را انتخاب کنید
3. برای پایه‌های دهم تا دوازدهم، رشته را انتخاب کنید
4. محصول مورد نظر را انتخاب کنید
5. روی "🛒 خرید" کلیک کنید
6. کد معرف خود را وارد کنید (اختیاری)
7. سفارش شما ثبت می‌شود

🎫 کد معرف:
• اگر کد معرف دارید: برای پیگیری فروش توسط نماینده
• اگر کد معرف ندارید: مستقیماً خرید به قیمت کاتالوگ

📞 پشتیبانی: @Arshya_Alaee"""


class PaymentMessages:
    """Payment related messages"""
    PAYMENT_INSTRUCTION_CASH = (
        "💳 مبلغ قابل پرداخت: {:,} تومان\n"
        "شماره کارت برای واریز: {} {}\n\n"
        "📸 لطفا اسکرین‌شات رسید واریزی را ارسال کنید.\n\n انصراف: /start"
    )
    
    PAYMENT_INSTRUCTION_INSTALLMENT = (
        "💳 مبلغ قسط اول را طبق مبلغ گفته شده در توضیحات محصول را واریز کنید\n"
        "شماره کارت برای واریز: {} {}\n\n"
        "📸 لطفا اسکرین‌شات رسید واریزی را ارسال کنید.\n\n انصراف: /start"
    )


# Button text constants
class ButtonTexts:
    """Button text constants for keyboards"""
    
    # Main menu buttons
    REGISTER = "👤 ثبت نام"
    LOTTERY = "🎲 قرعه کشی"
    PRODUCTS = "📚 خرید ویژه محصولات از نمایندگی 📚"
    HELP = "💡 راهنما"
    CONTACT = "💬 تماس با ما"
    BACK_TO_MENU = "🔙 بازگشت به منو"
    ALMAS_INSTALLMENT = "💎 خرید قسطی اشتراک الماس 💎"
    MY_INSTALLMENTS = "💳 اقساط من"
    FREE_CONSULTATION = "💬 مشاوره تلفنی رایگان"
    SUPPORT = "👩‍💻 پشتیبانی"
    COOPERATION = "🤝 همکاری با نمایندگی"
    INCOME_REFERRAL = "💰 درآمد زایی و معرفی دوستان"
    
    # Referral code buttons
    HAVE_REFERRAL = "کد معرف دارم"
    NO_REFERRAL = "کد معرف ندارم(تخفیف پیشفرض ربات)"
    
    # Payment method buttons
    PAYMENT_INSTALLMENT = "پرداخت قسطی"
    PAYMENT_CASH = "پرداخت نقدی"
    
    # Cities
    TEHRAN = "تهران"
    
    # Grades
    GRADE_5 = "پایه پنجم"
    GRADE_6 = "پایه ششم"
    GRADE_7 = "پایه هفتم"
    GRADE_8 = "پایه هشتم"
    GRADE_9 = "پایه نهم"
    GRADE_10 = "پایه دهم"
    GRADE_11 = "پایه یازدهم"
    GRADE_12 = "پایه دوازدهم"
    
    # Majors
    MATH = "ریاضی"
    SCIENCE = "تجربی"
    HUMANITIES = "انسانی"
    GENERAL = "عمومی"
    
    # Inline buttons
    BUY = "🛒 خرید"
    AUTHORIZE = "👤 ثبت نام"
    NOT_SURE = "هنوز مطمعن نیستم"
